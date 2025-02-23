static char help[] = "Poisson Problem in 2d and 3d with simplicial finite elements.\n\
We solve the Poisson problem in a rectangular\n\
domain, using a parallel unstructured mesh (DMPLEX) to discretize it.\n\n\n";

#include <iostream>
#include <petscdmplex.h>
#include <petscsnes.h>
#include <petscviewerhdf5.h>
#include <vtkSmartPointer.h>
#include <vtkPointData.h>
#include <vtkStructuredPoints.h>
#include <vtkDataSetReader.h>
#include <vtkPolyData.h>
#include <vtkPolyDataReader.h>
#include <vtkLandmarkTransform.h>

#define NUM_FIELDS 1
PetscInt spatialDim = 0;

//FIXME Hack
PetscScalar forcingconstant = 1.0;
PetscScalar coeffconstant = 1.0;

typedef enum {NEUMANN, DIRICHLET, NONE} BCType;
typedef enum {RUN_FULL, RUN_TEST, RUN_PERF} RunType;
typedef enum {COEFF_NONE, COEFF_ANALYTIC, COEFF_FIELD, COEFF_NONLINEAR} CoeffType;

typedef struct {
  PetscFEM      fem;               /* REQUIRED to use DMPlexComputeResidualFEM() */
  PetscInt      debug;             /* The debugging level */
  PetscMPIInt   rank;              /* The process rank */
  PetscMPIInt   numProcs;          /* The number of processes */
  RunType       runType;           /* Whether to run tests, or solve the full problem */
  PetscBool     jacobianMF;        /* Whether to calculate the Jacobian action on the fly */
  PetscLogEvent createMeshEvent;
  PetscBool     showInitial, showSolution, restart;
  PetscViewer   checkpoint;
  /* Domain and mesh definition */
  PetscInt      dim;               /* The topological mesh dimension */
  char          filename[2048];    /* The optional ExodusII file */
  char          imagefile[2048];   /* The vtk Image file */
  PetscBool     interpolate;       /* Generate intermediate mesh elements */
  PetscReal     refinementLimit;   /* The largest allowable cell volume */
  PetscBool     refinementUniform; /* Uniformly refine the mesh */
  PetscInt      refinementRounds;  /* The number of uniform refinements */
  char          partitioner[2048]; /* The graph partitioner */
  /* Element definition */
  PetscFE       fe[NUM_FIELDS];
  PetscFE       feBd[NUM_FIELDS];
  PetscFE       feAux[1];
  /* Problem definition */
  void (*f0Funcs[NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f0[]); /* f0_u(x,y,z), and f0_p(x,y,z) */
  void (*f1Funcs[NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f1[]); /* f1_u(x,y,z), and f1_p(x,y,z) */
  void (*g0Funcs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g0[]); /* g0_uu(x,y,z), g0_up(x,y,z), g0_pu(x,y,z), and g0_pp(x,y,z) */
  void (*g1Funcs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g1[]); /* g1_uu(x,y,z), g1_up(x,y,z), g1_pu(x,y,z), and g1_pp(x,y,z) */
  void (*g2Funcs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g2[]); /* g2_uu(x,y,z), g2_up(x,y,z), g2_pu(x,y,z), and g2_pp(x,y,z) */
  void (*g3Funcs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g3[]); /* g3_uu(x,y,z), g3_up(x,y,z), g3_pu(x,y,z), and g3_pp(x,y,z) */
  void (**exactFuncs)(const PetscReal x[], PetscScalar *u, void *ctx); /* The exact solution function u(x,y,z), v(x,y,z), and p(x,y,z) */
  void (*f0BdFuncs[NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar f0[]); /* f0_u(x,y,z), and f0_p(x,y,z) */
  void (*f1BdFuncs[NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar f1[]); /* f1_u(x,y,z), and f1_p(x,y,z) */
  void (*g0BdFuncs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar g0[]);
  void (*g1BdFuncs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar g1[]);
  void (*g2BdFuncs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar g2[]);
  void (*g3BdFuncs[NUM_FIELDS*NUM_FIELDS])(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar g3[]);
  BCType    bcType;
  CoeffType variableCoefficient;
  vtkSmartPointer<vtkLandmarkTransform> ApplicatorTransform ; 
  vtkSmartPointer<vtkImageData> ImageData ; 
} AppCtx;

void zero(const PetscReal coords[], PetscScalar *u, void *ctx)
{
  *u = 21.0;
}

void dirichletpotential(const PetscReal x[], PetscScalar *u, void *ctx)
{
  *u = 101.0;
}
/*
  In 2D for Dirichlet conditions, we use exact solution:

    u = x^2 + y^2
    f = 4

  so that

    -\Delta u + f = -4 + 4 = 0

  For Neumann conditions, we have

    -\nabla u \cdot -\hat y |_{y=0} =  (2y)|_{y=0} =  0 (bottom)
    -\nabla u \cdot  \hat y |_{y=1} = -(2y)|_{y=1} = -2 (top)
    -\nabla u \cdot -\hat x |_{x=0} =  (2x)|_{x=0} =  0 (left)
    -\nabla u \cdot  \hat x |_{x=1} = -(2x)|_{x=1} = -2 (right)

  Which we can express as

    \nabla u \cdot  \hat n|_\Gamma = {2 x, 2 y} \cdot \hat n = 2 (x + y)
*/
void quadratic_u_2d(const PetscReal x[], PetscScalar *u, void *ctx)
{
  *u = x[0]*x[0] + x[1]*x[1];
}

void f0_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f0[])
{
  f0[0] = 4.0;
}

void f0_bd_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar f0[])
{
  PetscInt  d;
  for (d = 0, f0[0] = 0.0; d < spatialDim; ++d) f0[0] += -n[d]*2.0*x[d];
}

void f0_bd_zero(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar f0[])
{
  f0[0] = 0.0;
}

void f1_bd_zero(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], const PetscReal n[], PetscScalar f1[])
{
  const PetscInt Ncomp = spatialDim;
  PetscInt       comp;

  for (comp = 0; comp < Ncomp; ++comp) f1[comp] = 0.0;
}

/* gradU[comp*dim+d] = {u_x, u_y} or {u_x, u_y, u_z} */
void f1_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f1[])
{
  PetscInt d;

  for (d = 0; d < spatialDim; ++d) f1[d] = gradU[d];
}

/* < \nabla v, \nabla u + {\nabla u}^T >
   This just gives \nabla u, give the perdiagonal for the transpose */
void g3_uu(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g3[])
{
  PetscInt d;

  for (d = 0; d < spatialDim; ++d) g3[d*spatialDim+d] = 1.0;
}

/*
  In 2D for Dirichlet conditions with a variable coefficient, we use exact solution:

    u  = x^2 + y^2
    f  = 6 (x + y)
    nu = (x + y)

  so that

    -\div \nu \grad u + f = -6 (x + y) + 6 (x + y) = 0
*/
void nu_2d(const PetscReal x[], PetscScalar *u, void *ctx)
{
 // *u = x[0] + x[1];
  AppCtx *user= (AppCtx*) ctx;

  double coord[3]= {x[0],x[1],x[2]};
  double pcoord[3];
  int    index[3];
  //transform the point and return the intensity value
  if ( user->ImageData->ComputeStructuredCoordinates(coord,index,pcoord) )
   {
     *u = coeffconstant * abs(user->ImageData->GetScalarComponentAsDouble(index[0],index[1],index[2],0));
   }
  else
   {
     *u = 0.5;
   }
   if(  *u < 1.e-5) * u = 0.5;
}

void f0_analytic_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f0[])
{
  //f0[0] = 6.0*(x[0] + x[1]);
  double applicator[3] = {.020,.175,.154};
  double radius = (applicator[0]-x[0])* (applicator[0]-x[0])
                + (applicator[1]-x[1])* (applicator[1]-x[1])
                + (applicator[2]-x[2])* (applicator[2]-x[2]);
  radius = sqrt(radius) + 1.e-6 ;
  f0[0]  = -forcingconstant*a[0]/radius/radius ;
  f0[0]  = -forcingconstant;
}

/* gradU[comp*dim+d] = {u_x, u_y} or {u_x, u_y, u_z} */
void f1_analytic_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f1[])
{
  PetscInt d;

  for (d = 0; d < spatialDim; ++d) f1[d] = (x[0] + x[1])*gradU[d];
}
void f1_field_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f1[])
{
  PetscInt d;

  for (d = 0; d < spatialDim; ++d) f1[d] = a[0]*gradU[d];
}

/* < \nabla v, \nabla u + {\nabla u}^T >
   This just gives \nabla u, give the perdiagonal for the transpose */
void g3_analytic_uu(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g3[])
{
  PetscInt d;

  for (d = 0; d < spatialDim; ++d) g3[d*spatialDim+d] = x[0] + x[1];
}
void g3_field_uu(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g3[])
{
  PetscInt d;

  //PetscPrintf(PETSC_COMM_WORLD, "coeff %f ...",a[0]);
  for (d = 0; d < spatialDim; ++d) g3[d*spatialDim+d] = a[0];
}

/*
  In 2D for Dirichlet conditions with a nonlinear coefficient (p-Laplacian with p = 4), we use exact solution:

    u  = x^2 + y^2
    f  = 16 (x^2 + y^2)
    nu = 1/2 |grad u|^2

  so that

    -\div \nu \grad u + f = -16 (x^2 + y^2) + 16 (x^2 + y^2) = 0
*/
void f0_analytic_nonlinear_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f0[])
{
  f0[0] = 16.0*(x[0]*x[0] + x[1]*x[1]);
}

/* gradU[comp*dim+d] = {u_x, u_y} or {u_x, u_y, u_z} */
void f1_analytic_nonlinear_u(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar f1[])
{
  PetscScalar nu = 0.0;
  PetscInt    d;
  for (d = 0; d < spatialDim; ++d) nu += gradU[d]*gradU[d];
  for (d = 0; d < spatialDim; ++d) f1[d] = 0.5*nu*gradU[d];
}

/*
  grad (u + eps w) - grad u = eps grad w

  1/2 |grad (u + eps w)|^2 grad (u + eps w) - 1/2 |grad u|^2 grad u
= 1/2 (|grad u|^2 + 2 eps <grad u,grad w>) (grad u + eps grad w) - 1/2 |grad u|^2 grad u
= 1/2 (eps |grad u|^2 grad w + 2 eps <grad u,grad w> grad u)
= eps (1/2 |grad u|^2 grad w + grad u <grad u,grad w>)
*/
void g3_analytic_nonlinear_uu(const PetscScalar u[], const PetscScalar gradU[], const PetscScalar a[], const PetscScalar gradA[], const PetscReal x[], PetscScalar g3[])
{
  PetscScalar nu = 0.0;
  PetscInt    d, e;
  for (d = 0; d < spatialDim; ++d) nu += gradU[d]*gradU[d];
  for (d = 0; d < spatialDim; ++d) {
    g3[d*spatialDim+d] = 0.5*nu;
    for (e = 0; e < spatialDim; ++e) {
      g3[d*spatialDim+e] += gradU[d]*gradU[e];
    }
  }
}

/*
  In 3D for Dirichlet conditions we use exact solution:

    u = x^2 + y^2 + z^2
    f = 6

  so that

    -\Delta u + f = -6 + 6 = 0

  For Neumann conditions, we have

    -\nabla u \cdot -\hat z |_{z=0} =  (2z)|_{z=0} =  0 (bottom)
    -\nabla u \cdot  \hat z |_{z=1} = -(2z)|_{z=1} = -2 (top)
    -\nabla u \cdot -\hat y |_{y=0} =  (2y)|_{y=0} =  0 (front)
    -\nabla u \cdot  \hat y |_{y=1} = -(2y)|_{y=1} = -2 (back)
    -\nabla u \cdot -\hat x |_{x=0} =  (2x)|_{x=0} =  0 (left)
    -\nabla u \cdot  \hat x |_{x=1} = -(2x)|_{x=1} = -2 (right)

  Which we can express as

    \nabla u \cdot  \hat n|_\Gamma = {2 x, 2 y, 2z} \cdot \hat n = 2 (x + y + z)
*/
void quadratic_u_3d(const PetscReal x[], PetscScalar *u, void *ctx)
{
  *u = x[0]*x[0] + x[1]*x[1] + x[2]*x[2];
}

#undef __FUNCT__
#define __FUNCT__ "ProcessOptions"
PetscErrorCode ProcessOptions(MPI_Comm comm, AppCtx *options)
{
  const char    *bcTypes[3]  = {"neumann", "dirichlet", "none"};
  const char    *runTypes[3] = {"full", "test", "perf"};
  const char    *coeffTypes[4] = {"none", "analytic", "field", "nonlinear"};
  PetscInt       bc, run, coeff;
  PetscBool      flg;
  PetscErrorCode ierr;

  PetscFunctionBeginUser;
  options->debug               = 1;
  options->runType             = RUN_FULL;
  options->dim                 = 2;
  options->filename[0]         = '\0';
  options->interpolate         = PETSC_FALSE;
  options->refinementLimit     = 0.0;
  options->refinementUniform   = PETSC_FALSE;
  options->refinementRounds    = 1;
  options->bcType              = DIRICHLET;
  options->variableCoefficient = COEFF_NONE;
  options->jacobianMF          = PETSC_FALSE;
  options->showInitial         = PETSC_FALSE;
  options->showSolution        = PETSC_FALSE;
  options->restart             = PETSC_FALSE;
  options->checkpoint          = NULL;

  options->fem.f0Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->f0Funcs;
  options->fem.f1Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->f1Funcs;
  options->fem.g0Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->g0Funcs;
  options->fem.g1Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->g1Funcs;
  options->fem.g2Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->g2Funcs;
  options->fem.g3Funcs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], PetscScalar[])) &options->g3Funcs;
  options->fem.f0BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->f0BdFuncs;
  options->fem.f1BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->f1BdFuncs;
  options->fem.g0BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->g0BdFuncs;
  options->fem.g1BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->g1BdFuncs;
  options->fem.g2BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->g2BdFuncs;
  options->fem.g3BdFuncs = (void (**)(const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscScalar[], const PetscReal[], const PetscReal[], PetscScalar[])) &options->g3BdFuncs;

  ierr = MPI_Comm_size(comm, &options->numProcs);CHKERRQ(ierr);
  ierr = MPI_Comm_rank(comm, &options->rank);CHKERRQ(ierr);
  ierr = PetscOptionsBegin(comm, "", "Poisson Problem Options", "DMPLEX");CHKERRQ(ierr);
  ierr = PetscOptionsInt("-debug", "The debugging level", "ex12.c", options->debug, &options->debug, NULL);CHKERRQ(ierr);
  run  = options->runType;
  ierr = PetscOptionsEList("-run_type", "The run type", "ex12.c", runTypes, 3, runTypes[options->runType], &run, NULL);CHKERRQ(ierr);

  options->runType = (RunType) run;

  ierr = PetscOptionsInt("-dim", "The topological mesh dimension", "ex12.c", options->dim, &options->dim, NULL);CHKERRQ(ierr);
  spatialDim = options->dim;
  ierr = PetscOptionsString("-f", "Exodus.II filename to read", "ex12.c", options->filename, options->filename, sizeof(options->filename), &flg);CHKERRQ(ierr);
#if !defined(PETSC_HAVE_EXODUSII)
  if (flg) SETERRQ(comm, PETSC_ERR_ARG_WRONG, "This option requires ExodusII support. Reconfigure using --download-exodusii");
#endif
  ierr = PetscOptionsBool("-interpolate", "Generate intermediate mesh elements", "ex12.c", options->interpolate, &options->interpolate, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsReal("-refinement_limit", "The largest allowable cell volume", "ex12.c", options->refinementLimit, &options->refinementLimit, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsBool("-refinement_uniform", "Uniformly refine the mesh", "ex52.c", options->refinementUniform, &options->refinementUniform, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsInt("-refinement_rounds", "The number of uniform refinements", "ex52.c", options->refinementRounds, &options->refinementRounds, NULL);CHKERRQ(ierr);
  ierr = PetscStrcpy(options->partitioner, "chaco");CHKERRQ(ierr);
  ierr = PetscOptionsString("-partitioner", "The graph partitioner", "pflotran.cxx", options->partitioner, options->partitioner, 2048, NULL);CHKERRQ(ierr);
  bc   = options->bcType;
  ierr = PetscOptionsEList("-bc_type","Type of boundary condition","ex12.c",bcTypes,3,bcTypes[options->bcType],&bc,NULL);CHKERRQ(ierr);
  options->bcType = (BCType) bc;
  coeff = options->variableCoefficient;
  ierr = PetscOptionsEList("-variable_coefficient","Type of variable coefficent","ex12.c",coeffTypes,4,coeffTypes[options->variableCoefficient],&coeff,NULL);CHKERRQ(ierr);
  options->variableCoefficient = (CoeffType) coeff;

  ierr = PetscOptionsBool("-jacobian_mf", "Calculate the action of the Jacobian on the fly", "ex12.c", options->jacobianMF, &options->jacobianMF, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsBool("-show_initial", "Output the initial guess for verification", "ex12.c", options->showInitial, &options->showInitial, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsBool("-show_solution", "Output the solution for verification", "ex12.c", options->showSolution, &options->showSolution, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsBool("-restart", "Read in the mesh and solution from a file", "ex12.c", options->restart, &options->restart, NULL);CHKERRQ(ierr);

  // read the image file ONCE
  ierr = PetscOptionsString("-vtk", "vtk filename to read", "ex12.c", options->imagefile, options->imagefile, sizeof(options->imagefile), &flg);CHKERRQ(ierr);
  if (flg)
     {
       ierr = PetscPrintf(PETSC_COMM_WORLD, "opening file...\n");CHKERRQ(ierr);
       vtkSmartPointer<vtkDataSetReader> reader = vtkSmartPointer<vtkDataSetReader>::New();
       reader->SetFileName(options->imagefile);
       reader->Update();
       // initilize the bounding data structure
       options->ImageData = vtkImageData::SafeDownCast( reader->GetOutput()) ;
     }
  else 
     {
       options->ImageData = 0;
     }
  char      sourcelandmarkfile[2048];   /* The vtk Image file */
  char      targetlandmarkfile[2048];   /* The vtk Image file */
  PetscBool sourceflg;
  PetscBool targetflg;
  ierr = PetscOptionsString("-sourcelandmark", "vtk filename to read", "ex12.c", sourcelandmarkfile, sourcelandmarkfile, sizeof(sourcelandmarkfile), &sourceflg);CHKERRQ(ierr);
  ierr = PetscOptionsString("-targetlandmark", "vtk filename to read", "ex12.c", targetlandmarkfile, targetlandmarkfile, sizeof(targetlandmarkfile), &targetflg);CHKERRQ(ierr);
  if (sourceflg && targetflg)
     {
       // read landmark files
       vtkSmartPointer<vtkPolyDataReader> SourceLMReader = vtkSmartPointer<vtkPolyDataReader>::New();
       vtkSmartPointer<vtkPolyDataReader> TargetLMReader = vtkSmartPointer<vtkPolyDataReader>::New();
       SourceLMReader->SetFileName(sourcelandmarkfile);
       TargetLMReader->SetFileName(targetlandmarkfile);
       SourceLMReader->Update();
       TargetLMReader->Update();

       // initialize transform
       options->ApplicatorTransform = vtkSmartPointer<vtkLandmarkTransform>::New();
       options->ApplicatorTransform->SetModeToRigidBody();
       options->ApplicatorTransform->SetSourceLandmarks( SourceLMReader->GetOutput()->GetPoints() );
       options->ApplicatorTransform->SetTargetLandmarks( TargetLMReader->GetOutput()->GetPoints() );
       options->ApplicatorTransform->Update();
       if(!options->rank) options->ApplicatorTransform->PrintSelf(std::cout,vtkIndent());
     }
  else 
     {
       options->ApplicatorTransform = 0;
     }
  // FIXME hack global variable
  ierr = PetscOptionsScalar("-forcingconstant", "forcing constant", "ex52.c", forcingconstant, &forcingconstant, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsScalar("-coeffconstant", "coefficent constant", "ex52.c", coeffconstant, &coeffconstant, NULL);CHKERRQ(ierr);
  ierr = PetscOptionsEnd();

  ierr = PetscLogEventRegister("CreateMesh", DM_CLASSID, &options->createMeshEvent);CHKERRQ(ierr);

  if (options->restart) {
    ierr = PetscViewerCreate(comm, &options->checkpoint);CHKERRQ(ierr);
    ierr = PetscViewerSetType(options->checkpoint, PETSCVIEWERHDF5);CHKERRQ(ierr);
    ierr = PetscViewerFileSetMode(options->checkpoint, FILE_MODE_READ);CHKERRQ(ierr);
    ierr = PetscViewerFileSetName(options->checkpoint, options->filename);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "CreateMesh"
PetscErrorCode CreateMesh(MPI_Comm comm, AppCtx *user, DM *dm)
{
  PetscInt       dim               = user->dim;
  const char    *filename          = user->filename;
  PetscBool      interpolate       = user->interpolate;
  PetscReal      refinementLimit   = user->refinementLimit;
  PetscBool      refinementUniform = user->refinementUniform;
  PetscInt       refinementRounds  = user->refinementRounds;
  const char    *partitioner       = user->partitioner;
  size_t         len;
  PetscErrorCode ierr;

  PetscFunctionBeginUser;
  ierr = PetscLogEventBegin(user->createMeshEvent,0,0,0,0);CHKERRQ(ierr);
  ierr = PetscStrlen(filename, &len);CHKERRQ(ierr);
  if (!len) {
    ierr = DMPlexCreateBoxMesh(comm, dim, interpolate, dm);CHKERRQ(ierr);
    ierr = PetscObjectSetName((PetscObject) *dm, "Mesh");CHKERRQ(ierr);
  } else if (user->checkpoint) {
    ierr = DMCreate(comm, dm);CHKERRQ(ierr);
    ierr = DMSetType(*dm, DMPLEX);CHKERRQ(ierr);
    ierr = DMLoad(*dm, user->checkpoint);CHKERRQ(ierr);
    ierr = DMPlexSetRefinementUniform(*dm, PETSC_FALSE);CHKERRQ(ierr);
  } else {
    PetscMPIInt rank;

    ierr = MPI_Comm_rank(comm, &rank);CHKERRQ(ierr);
    ierr = DMPlexCreateExodusFromFile(comm, filename, interpolate, dm);CHKERRQ(ierr);
    ierr = DMPlexSetRefinementUniform(*dm, PETSC_FALSE);CHKERRQ(ierr);
    /* Must have boundary marker for Dirichlet conditions */
    /* transform coordinates have boundary marker for Dirichlet conditions */
    if ( user->ApplicatorTransform ); 
      {
        Vec coordinates;  
        IS VertexNumbers;
        ierr = DMGetCoordinatesLocal(*dm, &coordinates);CHKERRQ(ierr);
        ierr = DMPlexGetVertexNumbering(*dm, &VertexNumbers);CHKERRQ(ierr);
        PetscScalar    *coords;
        ierr = VecGetArray(coordinates, &coords);CHKERRQ(ierr);
        PetscInt numVertices;
        ierr = ISGetSize(VertexNumbers, &numVertices);CHKERRQ(ierr);
        // FIXME single proc only
        ierr = PetscPrintf(PETSC_COMM_WORLD, "Vertex %d \n",numVertices);CHKERRQ(ierr);
        for (PetscInt v = 0; v < numVertices; ++v)  
          {
            // FIXME: assume 3d
            const double originalcoord[3]= {coords[v*dim+0],coords[v*dim+1],coords[v*dim+2]};
            double tranformcoord[3];
            user->ApplicatorTransform->TransformPoint(originalcoord,tranformcoord);
            //std::cout << originalcoord[0] << " " << originalcoord[1] << " " << originalcoord[2] << std::endl;
            //std::cout << tranformcoord[0] << " " << tranformcoord[1] << " " << tranformcoord[2] << std::endl;
            coords[v*dim+0] = tranformcoord[0];
            coords[v*dim+1] = tranformcoord[1];
            coords[v*dim+2] = tranformcoord[2];
          }
        ierr = VecRestoreArray(coordinates, &coords);CHKERRQ(ierr);
        ierr = PetscPrintf(PETSC_COMM_WORLD, "Transform Complete \n");CHKERRQ(ierr);
      }
  }
  {
    DM refinedMesh     = NULL;
    DM distributedMesh = NULL;

    /* Refine mesh using a volume constraint */
    ierr = DMPlexSetRefinementLimit(*dm, refinementLimit);CHKERRQ(ierr);
    ierr = DMRefine(*dm, comm, &refinedMesh);CHKERRQ(ierr);
    if (refinedMesh) {
      const char *name;

      ierr = PetscObjectGetName((PetscObject) *dm,         &name);CHKERRQ(ierr);
      ierr = PetscObjectSetName((PetscObject) refinedMesh,  name);CHKERRQ(ierr);
      ierr = DMDestroy(dm);CHKERRQ(ierr);
      *dm  = refinedMesh;
    }
    /* Distribute mesh over processes */
    ierr = DMPlexDistribute(*dm, partitioner, 0, NULL, &distributedMesh);CHKERRQ(ierr);
    if (distributedMesh) {
      ierr = DMDestroy(dm);CHKERRQ(ierr);
      *dm  = distributedMesh;
    }
    /* Use regular refinement in parallel */
    if (refinementUniform) {
      PetscInt r;

      ierr = DMPlexSetRefinementUniform(*dm, refinementUniform);CHKERRQ(ierr);
      for (r = 0; r < refinementRounds; ++r) {
        ierr = DMRefine(*dm, comm, &refinedMesh);CHKERRQ(ierr);
        if (refinedMesh) {
          ierr = DMDestroy(dm);CHKERRQ(ierr);
          *dm  = refinedMesh;
        }
      }
    }
  }
  ierr = DMSetFromOptions(*dm);CHKERRQ(ierr);
  ierr = DMViewFromOptions(*dm, NULL, "-dm_view");CHKERRQ(ierr);
  ierr = PetscLogEventEnd(user->createMeshEvent,0,0,0,0);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "SetupProblem"
PetscErrorCode SetupProblem(DM dm, AppCtx *user)
{
  PetscFEM *fem = &user->fem;

  PetscFunctionBeginUser;
  switch (user->variableCoefficient) {
  case COEFF_NONE:
    fem->f0Funcs[0] = f0_u;
    fem->f1Funcs[0] = f1_u;
    fem->g0Funcs[0] = NULL;
    fem->g1Funcs[0] = NULL;
    fem->g2Funcs[0] = NULL;
    fem->g3Funcs[0] = g3_uu;      /* < \nabla v, \nabla u > */
    break;
  case COEFF_ANALYTIC:
    fem->f0Funcs[0] = f0_analytic_u;
    fem->f1Funcs[0] = f1_analytic_u;
    fem->g0Funcs[0] = NULL;
    fem->g1Funcs[0] = NULL;
    fem->g2Funcs[0] = NULL;
    fem->g3Funcs[0] = g3_analytic_uu;
    break;
  case COEFF_FIELD:
    fem->f0Funcs[0] = f0_analytic_u;
    fem->f1Funcs[0] = f1_field_u;
    fem->g0Funcs[0] = NULL;
    fem->g1Funcs[0] = NULL;
    fem->g2Funcs[0] = NULL;
    fem->g3Funcs[0] = g3_field_uu;
    break;
  case COEFF_NONLINEAR:
    fem->f0Funcs[0] = f0_analytic_nonlinear_u;
    fem->f1Funcs[0] = f1_analytic_nonlinear_u;
    fem->g0Funcs[0] = NULL;
    fem->g1Funcs[0] = NULL;
    fem->g2Funcs[0] = NULL;
    fem->g3Funcs[0] = g3_analytic_nonlinear_uu;
    break;
  default: SETERRQ1(PETSC_COMM_SELF, PETSC_ERR_ARG_WRONG, "Invalid variable coefficient type %d", user->variableCoefficient);
  }
  fem->f0BdFuncs[0] = f0_bd_zero;
  fem->f1BdFuncs[0] = f1_bd_zero;
  fem->g0BdFuncs[0] = NULL;
  fem->g1BdFuncs[0] = NULL;
  fem->g2BdFuncs[0] = NULL;
  fem->g3BdFuncs[0] = NULL;
  switch (user->dim) {
  case 2:
    user->exactFuncs[0] = quadratic_u_2d;
    if (user->bcType == NEUMANN) fem->f0BdFuncs[0] = f0_bd_u;
    break;
  case 3:
    user->exactFuncs[0] = quadratic_u_3d;
    if (user->bcType == NEUMANN) fem->f0BdFuncs[0] = f0_bd_u;
    break;
  default:
    SETERRQ1(PETSC_COMM_WORLD, PETSC_ERR_ARG_OUTOFRANGE, "Invalid dimension %d", user->dim);
  }
  user->fem.bcFuncs = NULL;
  user->fem.bcCtxs  = NULL;
  PetscFunctionReturn(0);
}

/*
Matthew Knepley
Mar 31 to me, Geoffrey, For 
On Mon, Mar 31, 2014 at 9:27 AM, David Fuentes <fuentesdt@gmail.com> wrote:
> Hi,
> 
> I'm trying to get DMPlex to solve and display with Dirichlet boundary conditions.
> 
> My global and local solution vectors are of different sizes. The length
> difference is the number of nodes read from the nodeset read in the exodus
> file.  I am able to project the initial solution/boundary data that I want
> with with VecSetValuesSection. The initial condition looks ok with the global
> solution in the viewer. However, I seem to be losing the dirichlet boundary
> data on the solve ? I'm trying to use the suggested global to local
> scattering on the output.

I have just worked all this out in 'next', and most of it is in 'master' now. I will talk through the process

1) Suppose you view a global vector, either VTK or HDF5

2) PETSc maps this to a local vector, and calls the local version, which is the same as viewing a local vector

3) PETSc will insert the correct boundary values (via DMPlexInsertBoundaryValuesFEM) if you specify them
    using the Section interface + DMPlexAddBoundary(). Otherwise, you can view a local vector with the correct boundary values.

4) A scatter is created to a global vector including the boundary values

5) This expanded global vector is passes to the normal HDF5/VTK routines

*/
#undef __FUNCT__
#define __FUNCT__ "SetupSection"
PetscErrorCode SetupSection(DM dm, AppCtx *user)
{
  DM             cdm = dm;
  const PetscInt nodeSetApplicatorValue = 2; // node set value assigned to exodus mesh
  const PetscInt nodeSetBoundaryValue = 3; // node set value assigned to exodus mesh
  PetscErrorCode ierr;

  PetscFunctionBeginUser;
  ierr = PetscObjectSetName((PetscObject) user->fe[0], "temperature");CHKERRQ(ierr);
  while (cdm) {
    ierr = DMSetNumFields(cdm, 1);CHKERRQ(ierr);
    ierr = DMSetField(cdm, 0, (PetscObject) user->fe[0]);CHKERRQ(ierr);
    PetscBool dirichletType = PETSC_FALSE;
    if  (user->bcType == DIRICHLET) dirichletType = PETSC_TRUE;
    // TODO: for exodus mesh, the node set name is ignored and identified by integer nodeSetValue
    // TODO: function pointers specify the boundary value
    //ierr = DMPlexAddBoundary(cdm, dirichletType , user->bcType == NEUMANN ? "boundary" : "Vertex Sets", 0, (void (*)())dirichletpotential, 1, &nodeSetApplicatorValue , user);CHKERRQ(ierr);
    ierr = DMPlexAddBoundary(cdm, dirichletType , user->bcType == NEUMANN ? "boundary" : "Vertex Sets", 0, (void (*)())zero, 1, &nodeSetBoundaryValue , user);CHKERRQ(ierr);
    ierr = DMPlexGetCoarseDM(cdm, &cdm);CHKERRQ(ierr);
  }
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "SetupMaterialSection"
PetscErrorCode SetupMaterialSection(DM dm, AppCtx *user)
{
  PetscSection    section;
  PetscInt        dim   = user->dim;
  PetscInt        numBC = 0;
  PetscInt        numComp[1];
  const PetscInt *numDof;
  PetscErrorCode  ierr;

  PetscFunctionBeginUser;
  if (user->variableCoefficient != COEFF_FIELD) PetscFunctionReturn(0);
  ierr = PetscFEGetNumComponents(user->feAux[0], &numComp[0]);CHKERRQ(ierr);
  ierr = PetscFEGetNumDof(user->feAux[0], &numDof);CHKERRQ(ierr);
  ierr = DMPlexCreateSection(dm, dim, 1, numComp, numDof, numBC, NULL, NULL, NULL, &section);CHKERRQ(ierr);
  ierr = DMSetDefaultSection(dm, section);CHKERRQ(ierr);
  ierr = PetscSectionDestroy(&section);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "SetupMaterial"
PetscErrorCode SetupMaterial(DM dm, DM dmAux, AppCtx *user)
{
  void (*matFuncs[1])(const PetscReal x[], PetscScalar *u, void *ctx) = {nu_2d};
  Vec            nu;
  PetscErrorCode ierr;

  PetscFunctionBegin;
  if (user->variableCoefficient != COEFF_FIELD) PetscFunctionReturn(0);
  ierr = DMCreateLocalVector(dmAux, &nu);CHKERRQ(ierr);
  ierr = DMPlexProjectFunctionLocal(dmAux, user->feAux, matFuncs, ((void**)&user), INSERT_ALL_VALUES, nu);CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject) dm, "dmAux", (PetscObject) dmAux);CHKERRQ(ierr);
  ierr = PetscObjectCompose((PetscObject) dm, "A", (PetscObject) nu);CHKERRQ(ierr);
  ierr = VecDestroy(&nu);CHKERRQ(ierr);
  PetscFunctionReturn(0);
}

#undef __FUNCT__
#define __FUNCT__ "main"
int main(int argc, char **argv)
{
  DM             dm;          /* Problem specification */
  DM             dmAux;       /* Material specification */
  SNES           snes;        /* nonlinear solver */
  Vec            u,r;         /* solution, residual vectors */
  Mat            A,J;         /* Jacobian matrix */
  MatNullSpace   nullSpace;   /* May be necessary for Neumann conditions */
  AppCtx         user;        /* user-defined work context */
  JacActionCtx   userJ;       /* context for Jacobian MF action */
  PetscInt       its;         /* iterations for convergence */
  PetscReal      error = 0.0; /* L_2 error in the solution */
  PetscInt       numComponents;
  PetscBool      write_output=PETSC_TRUE;
  PetscErrorCode ierr;

  ierr = PetscInitialize(&argc, &argv, NULL, help);CHKERRQ(ierr);
  ierr = ProcessOptions(PETSC_COMM_WORLD, &user);CHKERRQ(ierr);
  ierr = SNESCreate(PETSC_COMM_WORLD, &snes);CHKERRQ(ierr);
  ierr = CreateMesh(PETSC_COMM_WORLD, &user, &dm);CHKERRQ(ierr);
  ierr = SNESSetDM(snes, dm);CHKERRQ(ierr);
  ierr = DMSetApplicationContext(dm, &user);CHKERRQ(ierr);

  user.fem.fe = user.fe;
  ierr = PetscFECreateDefault(dm, user.dim, 1, PETSC_TRUE, NULL, -1, &user.fe[0]);CHKERRQ(ierr);
  if (user.bcType != NEUMANN) {
    user.fem.feBd = NULL; user.feBd[0] = NULL;
  } else {
    user.fem.feBd = user.feBd;
    ierr = PetscFECreateDefault(dm, user.dim-1, 1, PETSC_TRUE, "bd_", -1, &user.feBd[0]);CHKERRQ(ierr);
  }
  ierr = PetscFEGetNumComponents(user.fe[0], &numComponents);CHKERRQ(ierr);
  ierr = PetscMalloc(NUM_FIELDS * sizeof(void (*)(const PetscReal[], PetscScalar *, void *)), &user.exactFuncs);CHKERRQ(ierr);
  ierr = SetupProblem(dm, &user);CHKERRQ(ierr);
  ierr = SetupSection(dm, &user);CHKERRQ(ierr);
  /* Setup Material */
  ierr = DMClone(dm, &dmAux);CHKERRQ(ierr);
  ierr = DMPlexCopyCoordinates(dm, dmAux);CHKERRQ(ierr);
  if (user.variableCoefficient != COEFF_FIELD) {
    user.fem.feAux = NULL; user.feAux[0] = NULL;
  } else {
    PetscQuadrature q;

    user.fem.feAux = user.feAux;
    ierr = PetscFECreateDefault(dmAux, user.dim, 1, PETSC_TRUE, "mat_", -1, &user.feAux[0]);CHKERRQ(ierr);
    ierr = PetscFEGetQuadrature(user.fe[0], &q);CHKERRQ(ierr);
    ierr = PetscFESetQuadrature(user.feAux[0], q);CHKERRQ(ierr);
  }
  ierr = SetupMaterialSection(dmAux, &user);CHKERRQ(ierr);
  ierr = SetupMaterial(dm, dmAux, &user);CHKERRQ(ierr);
  ierr = DMDestroy(&dmAux);CHKERRQ(ierr);

  ierr = DMCreateGlobalVector(dm, &u);CHKERRQ(ierr);
  ierr = PetscObjectSetName((PetscObject) u, "temperature");CHKERRQ(ierr);
  ierr = VecDuplicate(u, &r);CHKERRQ(ierr);

  ierr = DMSetMatType(dm,MATAIJ);CHKERRQ(ierr);
  ierr = DMCreateMatrix(dm, &J);CHKERRQ(ierr);
  if (user.jacobianMF) {
    PetscInt M, m, N, n;

    ierr = MatGetSize(J, &M, &N);CHKERRQ(ierr);
    ierr = MatGetLocalSize(J, &m, &n);CHKERRQ(ierr);
    ierr = MatCreate(PETSC_COMM_WORLD, &A);CHKERRQ(ierr);
    ierr = MatSetSizes(A, m, n, M, N);CHKERRQ(ierr);
    ierr = MatSetType(A, MATSHELL);CHKERRQ(ierr);
    ierr = MatSetUp(A);CHKERRQ(ierr);
#if 0
    ierr = MatShellSetOperation(A, MATOP_MULT, (void (*)(void))FormJacobianAction);CHKERRQ(ierr);
#endif

    userJ.dm   = dm;
    userJ.J    = J;
    userJ.user = &user;

    ierr = DMCreateLocalVector(dm, &userJ.u);CHKERRQ(ierr);
    ierr = DMPlexProjectFunctionLocal(dm, user.fe, user.exactFuncs, NULL, INSERT_BC_VALUES, userJ.u);CHKERRQ(ierr);
    ierr = MatShellSetContext(A, &userJ);CHKERRQ(ierr);
  } else {
    A = J;
  }
  if (user.bcType == NEUMANN) {
    ierr = MatNullSpaceCreate(PetscObjectComm((PetscObject) dm), PETSC_TRUE, 0, NULL, &nullSpace);CHKERRQ(ierr);
    ierr = MatSetNullSpace(J, nullSpace);CHKERRQ(ierr);
    if (A != J) {
      ierr = MatSetNullSpace(A, nullSpace);CHKERRQ(ierr);
    }
  }

  ierr = DMSNESSetFunctionLocal(dm,  (PetscErrorCode (*)(DM,Vec,Vec,void*)) DMPlexComputeResidualFEM, &user);CHKERRQ(ierr);
  ierr = DMSNESSetJacobianLocal(dm,  (PetscErrorCode (*)(DM,Vec,Mat,Mat,void*)) DMPlexComputeJacobianFEM, &user);CHKERRQ(ierr);
  ierr = SNESSetJacobian(snes, A, J, NULL, NULL);CHKERRQ(ierr);

  ierr = SNESSetFromOptions(snes);CHKERRQ(ierr);

  ierr = DMPlexProjectFunction(dm, user.fe, user.exactFuncs, NULL, INSERT_ALL_VALUES, u);CHKERRQ(ierr);
  if (user.checkpoint) {
#if defined(PETSC_HAVE_HDF5)
    ierr = PetscViewerHDF5PushGroup(user.checkpoint, "/fields");CHKERRQ(ierr);
    ierr = VecLoad(u, user.checkpoint);CHKERRQ(ierr);
    ierr = PetscViewerHDF5PopGroup(user.checkpoint);CHKERRQ(ierr);
#endif
  }
  ierr = PetscViewerDestroy(&user.checkpoint);CHKERRQ(ierr);
  if (user.showInitial) {
    Vec lv;
    ierr = DMGetLocalVector(dm, &lv);CHKERRQ(ierr);
    ierr = DMGlobalToLocalBegin(dm, u, INSERT_VALUES, lv);CHKERRQ(ierr);
    ierr = DMGlobalToLocalEnd(dm, u, INSERT_VALUES, lv);CHKERRQ(ierr);
    ierr = DMPrintLocalVec(dm, "Local function", 1.0e-10, lv);CHKERRQ(ierr);
    ierr = DMRestoreLocalVector(dm, &lv);CHKERRQ(ierr);
  }
  if (user.runType == RUN_FULL) {
    void (*initialGuess[numComponents])(const PetscReal x[], PetscScalar *, void *ctx);
    PetscInt c;

    // zero out 
    for (c = 0; c < numComponents; ++c) initialGuess[c] = zero;
    ierr = DMPlexProjectFunction(dm, user.fe, initialGuess, NULL, INSERT_VALUES, u);CHKERRQ(ierr);
    if (write_output) {
      ierr = PetscPrintf(PETSC_COMM_WORLD, "Initial guess\n");CHKERRQ(ierr);
      PetscViewer viewer;
      char               vtkfilename[PETSC_MAX_PATH_LEN] = "solution.0000.vtk";
      ierr = PetscViewerVTKOpen(PETSC_COMM_WORLD,vtkfilename,FILE_MODE_WRITE,&viewer);CHKERRQ(ierr);
      ierr = VecView(u,viewer);CHKERRQ(ierr);
      ierr = PetscViewerDestroy(&viewer);CHKERRQ(ierr);
    }
    // -petscfe_type opencl ==> PetscFEIntegrateResidual_OpenCL
    ierr = SNESSolve(snes, NULL, u);CHKERRQ(ierr);
    ierr = SNESGetIterationNumber(snes, &its);CHKERRQ(ierr);
    ierr = PetscPrintf(PETSC_COMM_WORLD, "Number of SNES iterations = %D\n", its);CHKERRQ(ierr);
    ierr = DMPlexComputeL2Diff(dm, user.fe, user.exactFuncs, NULL, u, &error);CHKERRQ(ierr);
    if (error < 1.0e-11) {ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Error: < 1.0e-11\n");CHKERRQ(ierr);}
    else                 {ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Error: %g\n", error);CHKERRQ(ierr);}
    if (user.showSolution) {
      ierr = PetscPrintf(PETSC_COMM_WORLD, "Solution\n");CHKERRQ(ierr);
      ierr = VecChop(u, 3.0e-9);CHKERRQ(ierr);
      ierr = VecView(u, PETSC_VIEWER_STDOUT_WORLD);CHKERRQ(ierr);
    }
  } else if (user.runType == RUN_PERF) {
    PetscReal res = 0.0;

    ierr = SNESComputeFunction(snes, u, r);CHKERRQ(ierr);
    ierr = PetscPrintf(PETSC_COMM_WORLD, "Initial Residual\n");CHKERRQ(ierr);
    ierr = VecChop(r, 1.0e-10);CHKERRQ(ierr);
    ierr = VecNorm(r, NORM_2, &res);CHKERRQ(ierr);
    ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Residual: %g\n", res);CHKERRQ(ierr);
  } else {
    PetscReal res = 0.0;

    /* Check discretization error */
    ierr = PetscPrintf(PETSC_COMM_WORLD, "Initial guess\n");CHKERRQ(ierr);
    ierr = VecView(u, PETSC_VIEWER_STDOUT_WORLD);CHKERRQ(ierr);
    ierr = DMPlexComputeL2Diff(dm, user.fe, user.exactFuncs, NULL, u, &error);CHKERRQ(ierr);
    if (error < 1.0e-11) {ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Error: < 1.0e-11\n");CHKERRQ(ierr);}
    else                 {ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Error: %g\n", error);CHKERRQ(ierr);}
    /* Check residual */
    ierr = SNESComputeFunction(snes, u, r);CHKERRQ(ierr);
    ierr = PetscPrintf(PETSC_COMM_WORLD, "Initial Residual\n");CHKERRQ(ierr);
    ierr = VecChop(r, 1.0e-10);CHKERRQ(ierr);
    ierr = VecView(r, PETSC_VIEWER_STDOUT_WORLD);CHKERRQ(ierr);
    ierr = VecNorm(r, NORM_2, &res);CHKERRQ(ierr);
    ierr = PetscPrintf(PETSC_COMM_WORLD, "L_2 Residual: %g\n", res);CHKERRQ(ierr);
    /* Check Jacobian */
    {
      Vec          b;

      ierr = SNESComputeJacobian(snes, u, A, A);CHKERRQ(ierr);
      ierr = VecDuplicate(u, &b);CHKERRQ(ierr);
      ierr = VecSet(r, 0.0);CHKERRQ(ierr);
      ierr = SNESComputeFunction(snes, r, b);CHKERRQ(ierr);
      ierr = MatMult(A, u, r);CHKERRQ(ierr);
      ierr = VecAXPY(r, 1.0, b);CHKERRQ(ierr);
      ierr = VecDestroy(&b);CHKERRQ(ierr);
      ierr = PetscPrintf(PETSC_COMM_WORLD, "Au - b = Au + F(0)\n");CHKERRQ(ierr);
      ierr = VecChop(r, 1.0e-10);CHKERRQ(ierr);
      ierr = VecView(r, PETSC_VIEWER_STDOUT_WORLD);CHKERRQ(ierr);
      ierr = VecNorm(r, NORM_2, &res);CHKERRQ(ierr);
      ierr = PetscPrintf(PETSC_COMM_WORLD, "Linear L_2 Residual: %g\n", res);CHKERRQ(ierr);
    }
  }
  ierr = VecViewFromOptions(u, NULL, "-vec_view");CHKERRQ(ierr);

  if (write_output) {
    PetscViewer viewer;
    char               vtkfilename[PETSC_MAX_PATH_LEN] = "solution.0001.vtk";
    ierr = PetscViewerVTKOpen(PETSC_COMM_WORLD,vtkfilename,FILE_MODE_WRITE,&viewer);CHKERRQ(ierr);
    ierr = VecView(u,viewer);CHKERRQ(ierr);
    ierr = PetscViewerDestroy(&viewer);CHKERRQ(ierr);
  }
  // FIXME : view material from global vector ? A is a local vector ?
  if (write_output) {
    PetscViewer viewer;
    Vec            localnu,globalnu; // local and global vectors
    DM             tmpAux;       /* Material specification */
    ierr = PetscObjectQuery((PetscObject) dm, "dmAux", (PetscObject *) &tmpAux);CHKERRQ(ierr);
    ierr = DMSetField(tmpAux, 0, (PetscObject) user.feAux[0]);CHKERRQ(ierr);
    ierr = DMCreateGlobalVector(tmpAux, &globalnu);CHKERRQ(ierr);
    ierr = PetscObjectQuery((PetscObject) dm, "A", (PetscObject *) &localnu);CHKERRQ(ierr);
    char               vtkfilename[PETSC_MAX_PATH_LEN] = "material.vtk";
    // scatter material to u
    ierr = DMLocalToGlobalBegin(dm, localnu, INSERT_VALUES, globalnu);CHKERRQ(ierr);
    ierr = DMLocalToGlobalEnd(dm, localnu, INSERT_VALUES, globalnu);CHKERRQ(ierr);
    ierr = PetscViewerVTKOpen(PETSC_COMM_WORLD,vtkfilename,FILE_MODE_WRITE,&viewer);CHKERRQ(ierr);
    // FIXME : should I be viewing from the global vector ? 
    ierr = VecView(localnu,viewer);CHKERRQ(ierr);
    ierr = PetscViewerDestroy(&viewer);CHKERRQ(ierr);
    ierr = VecDestroy(&globalnu);CHKERRQ(ierr);
  }

  if (user.bcType == NEUMANN) {
    ierr = MatNullSpaceDestroy(&nullSpace);CHKERRQ(ierr);
  }
  if (user.jacobianMF) {
    ierr = VecDestroy(&userJ.u);CHKERRQ(ierr);
  }
  if (A != J) {ierr = MatDestroy(&A);CHKERRQ(ierr);}
  ierr = PetscFEDestroy(&user.fe[0]);CHKERRQ(ierr);
  ierr = PetscFEDestroy(&user.feBd[0]);CHKERRQ(ierr);
  ierr = PetscFEDestroy(&user.feAux[0]);CHKERRQ(ierr);
  ierr = MatDestroy(&J);CHKERRQ(ierr);
  ierr = VecDestroy(&u);CHKERRQ(ierr);
  ierr = VecDestroy(&r);CHKERRQ(ierr);
  ierr = SNESDestroy(&snes);CHKERRQ(ierr);
  ierr = DMDestroy(&dm);CHKERRQ(ierr);
  ierr = PetscFree(user.exactFuncs);CHKERRQ(ierr);
  ierr = PetscFinalize();
  return 0;
}
