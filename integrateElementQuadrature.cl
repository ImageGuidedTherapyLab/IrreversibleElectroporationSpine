__kernel void integrateElementQuadrature(int N_cb, __global float *coefficients, __global float *coefficientsAux, __global float *jacobianInverses, __global float *jacobianDeterminants, __global float *elemVec)
{
  // generated from PetscFEOpenCLGenerateIntegrationCode
  // from gdb
  //    call printf("%s",buffer);

  /* Quadrature points
   - (x1,y1,x2,y2,...) */
  const float points[3] = {
-0.5,
-0.5,
-0.5,
};
  /* Quadrature weights
   - (v1,v2,...) */
  const float weights[1] = {
1.33333,
};
  /* Nodal basis function evaluations
    - basis component is fastest varying, the basis function, then point */
  const float Basis[4] = {
0.25,
0.25,
0.25,
0.25,
};

  /* Nodal basis function derivative evaluations,
      - derivative direction is fastest varying, then basis component, then basis function, then point */
  const float3 BasisDerivatives[4] = {
(float3)(-0.5, -0.5, -0.5),
(float3)(0, 0.5, 0),
(float3)(0.5, 0, 0),
(float3)(0, 0, 0.5),
};
  const int dim    = 3;                           // The spatial dimension
  const int N_bl   = 2;                           // The number of concurrent blocks
  const int N_b    = 4;                           // The number of basis functions
  const int N_comp = 1;                           // The number of basis function components
  const int N_bt   = N_b*N_comp;                    // The total number of scalar basis functions
  const int N_q    = 1;                           // The number of quadrature points
  const int N_bst  = N_bt*N_q;                      // The block size, LCM(N_b*N_comp, N_q), Notice that a block is not processed simultaneously
  const int N_t    = N_bst*N_bl;                    // The number of threads, N_bst * N_bl
  const int N_bc   = N_t/N_comp;                    // The number of cells per batch (N_b*N_q*N_bl)
  const int N_sbc  = N_bst / (N_q * N_comp);
  const int N_sqc  = N_bst / N_bt;
  /*const int N_c    = N_cb * N_bc;*/

  /* Calculated indices */
  /*const int tidx    = get_local_id(0) + get_local_size(0)*get_local_id(1);*/
  const int tidx    = get_local_id(0);
  const int blidx   = tidx / N_bst;                  // Block number for this thread
  const int bidx    = tidx % N_bt;                   // Basis function mapped to this thread
  const int cidx    = tidx % N_comp;                 // Basis component mapped to this thread
  const int qidx    = tidx % N_q;                    // Quadrature point mapped to this thread
  const int blbidx  = tidx % N_q + blidx*N_q;        // Cell mapped to this thread in the basis phase
  const int blqidx  = tidx % N_b + blidx*N_b;        // Cell mapped to this thread in the quadrature phase
  const int gidx    = get_group_id(1)*get_num_groups(0) + get_group_id(0);

  /* Quadrature data */
  float                w;                   // $w_q$, Quadrature weight at $x_q$
  __local float         phi_i[4];    //[N_bt*N_q];  // $\phi_i(x_q)$, Value of the basis function $i$ at $x_q$
  __local float3       phiDer_i[4]; //[N_bt*N_q];  // $\frac{\partial\phi_i(x_q)}{\partial x_d}$, Value of the derivative of basis function $i$ in direction $x_d$ at $x_q$
  /* Geometric data */
  __local float        detJ[8]; //[N_t];           // $|J(x_q)|$, Jacobian determinant at $x_q$
  __local float        invJ[72];//[N_t*dim*dim];   // $J^{-1}(x_q)$, Jacobian inverse at $x_q$
  /* FEM data */
  __local float        u_i[32]; //[N_t*N_bt];       // Coefficients $u_i$ of the field $u|_{\mathcal{T}} = \sum_i u_i \phi_i$
  __local float        a_i[8]; //[N_t];            // Coefficients $a_i$ of the auxiliary field $a|_{\mathcal{T}} = \sum_i a_i \phi^R_i$
  /* Intermediate calculations */
  __local float         f_0[8]; //[N_t*N_sqc];      // $f_0(u(x_q), \nabla u(x_q)) |J(x_q)| w_q$
  __local float3       f_1[8]; //[N_t*N_sqc];      // $f_1(u(x_q), \nabla u(x_q)) |J(x_q)| w_q$
  /* Output data */
  float                e_i;                 // Coefficient $e_i$ of the residual

  /* These should be generated inline */
  /* Load quadrature weights */
  w = weights[qidx];
  /* Load basis tabulation \phi_i for this cell */
  if (tidx < N_bt*N_q) {
    phi_i[tidx]    = Basis[tidx];
    phiDer_i[tidx] = BasisDerivatives[tidx];
  }

  for (int batch = 0; batch < N_cb; ++batch) {
    const int Goffset = gidx*N_cb*N_bc;
    /* Load geometry */
    detJ[tidx] = jacobianDeterminants[Goffset+batch*N_bc+tidx];
    for (int n = 0; n < dim*dim; ++n) {
      const int offset = n*N_t;
      invJ[offset+tidx] = jacobianInverses[(Goffset+batch*N_bc)*dim*dim+offset+tidx];
    }
    /* Load coefficients u_i for this cell */
    for (int n = 0; n < N_bt; ++n) {
      const int offset = n*N_t;
      u_i[offset+tidx] = coefficients[(Goffset*N_bt)+batch*N_t*N_b+offset+tidx];
    }
    /* Load coefficients a_i for this cell */
    /* TODO: This should not be N_t here, it should be N_bc*N_comp_aux */
    a_i[tidx] = coefficientsAux[Goffset+batch*N_t+tidx];

    /* Map coefficients to values at quadrature points */
    for (int c = 0; c < N_sqc; ++c) {
      const int cell          = c*N_bl*N_b + blqidx;
      const int fidx          = (cell*N_q + qidx)*N_comp + cidx;
      float3   gradU[1]; //[N_comp]; // $\nabla u(x_q)$, Value of the field gradient at $x_q$
      float  a[1]; //[1];     // $a(x_q)$, Value of the auxiliary fields at $x_q$

      for (int comp = 0; comp < N_comp; ++comp) {
        gradU[comp].x = 0.0; gradU[comp].y = 0.0; gradU[comp].z = 0.0;
      }
      a[0] = 0.0;
      /* Get field and derivatives at this quadrature point */
      for (int i = 0; i < N_b; ++i) {
        for (int comp = 0; comp < N_comp; ++comp) {
          const int b    = i*N_comp+comp;
          const int pidx = qidx*N_bt + b;
          const int uidx = cell*N_bt + b;
          float3   realSpaceDer;

          realSpaceDer.x = invJ[cell*dim*dim+0*dim+0]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+0]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+0]*phiDer_i[pidx].z;
          gradU[comp].x += u_i[uidx]*realSpaceDer.x;
          realSpaceDer.y = invJ[cell*dim*dim+0*dim+1]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+1]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+1]*phiDer_i[pidx].z;
          gradU[comp].y += u_i[uidx]*realSpaceDer.y;
          realSpaceDer.z = invJ[cell*dim*dim+0*dim+2]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+2]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+2]*phiDer_i[pidx].z;
          gradU[comp].z += u_i[uidx]*realSpaceDer.z;
        }
      }
          a[0] += a_i[cell];
      /* Process values at quadrature points */
      f_0[fidx] = 4.0;
      f_1[fidx] = a[cell]*gradU[cidx];
      f_0[fidx] *= detJ[cell]*w;
      f_1[fidx].x *= detJ[cell]*w; f_1[fidx].y *= detJ[cell]*w; f_1[fidx].z *= detJ[cell]*w;
    }

    /* ==== TRANSPOSE THREADS ==== */
    barrier(CLK_GLOBAL_MEM_FENCE);

    /* Map values at quadrature points to coefficients */
    for (int c = 0; c < N_sbc; ++c) {
      const int cell = c*N_bl*N_q + blbidx;

      e_i = 0.0;
      for (int q = 0; q < N_q; ++q) {
        const int pidx = q*N_bt + bidx;
        const int fidx = (cell*N_q + q)*N_comp + cidx;
        float3   realSpaceDer;

        e_i += phi_i[pidx]*f_0[fidx];
        realSpaceDer.x = invJ[cell*dim*dim+0*dim+0]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+0]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+0]*phiDer_i[pidx].z;
        e_i           += realSpaceDer.x*f_1[fidx].x;
        realSpaceDer.y = invJ[cell*dim*dim+0*dim+1]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+1]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+1]*phiDer_i[pidx].z;
        e_i           += realSpaceDer.y*f_1[fidx].y;
        realSpaceDer.z = invJ[cell*dim*dim+0*dim+2]*phiDer_i[pidx].x + invJ[cell*dim*dim+1*dim+2]*phiDer_i[pidx].y + invJ[cell*dim*dim+2*dim+2]*phiDer_i[pidx].z;
        e_i           += realSpaceDer.z*f_1[fidx].z;
      }
      /* Write element vector for N_{cbc} cells at a time */
      elemVec[(gidx*N_cb*N_bc*N_bt)+(batch*N_sbc+c)*N_t+tidx] = e_i;
    }
    /* ==== Could do one write per batch ==== */
  }
  return;
}
