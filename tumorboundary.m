
clear all 
close all


syms A1 B1 R1 R2 R3 A2 B2 phi0 sigma1 sigma2

% phi1(r) = A1/r + B1     phi1(R1) = phi0    phi1(R2) = phi2(R2)
% phi2(r) = A2/r + B2     sigma1 d/dr phi1(R2) = sigma2 d/dr phi2(R2)          phi2(R3) = 0

A = [1/R1 1 0 0 ; -sigma1/R2 0 sigma2/R2 0 ; 1/R2 1 -1/R2 -1; 0 0 1/R3 1];
b = [ phi0 ;0 ;0;0];


x = A\b
