
clear all 
close all


syms A1 B1 R1 R2 R3 A2 B2 phi0 sigma1 sigma2

% phi1(r) = A1/r + B1     phi1(R1) = phi0    phi1(R2) = phi2(R2)
% phi2(r) = A2/r + B2     sigma1 d/dr phi1(R2) = sigma2 d/dr phi2(R2)          phi2(R3) = 0

A = [1/R1 1 0 0 ; -sigma1 0 sigma2 0 ; 1/R2 1 -1/R2 -1; 0 0 1/R3 1];
b = [ phi0 ;0 ;0;0];


x = A\b

%% x =
%% 
%%                             -(R1*R2*R3*phi0*sigma2)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2)
%% (phi0*(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2))/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2)
%%                             -(R1*R2*R3*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2)
%%                                 (R1*R2*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2)
%% 

phi0 = 1000, sigma1 = 1, sigma2=.1, R1 = .001, R2 = .01, R3 = .05;
A1=                             -(R1*R2*R3*phi0*sigma2)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
B1= (phi0*(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2))/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
A2=                             -(R1*R2*R3*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
B2=                                 (R1*R2*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);

radius1= [R1:.0005:R2];
phi1= radius1.^(-1)*A1 +B1;
dphi1dr=-radius1.^(-2)*A1;
 
radius2= [R2:.0005:R3];
phi2= radius2.^(-1)*A2 +B2;
dphi2dr=-radius2.^(-2)*A2;

figure(1)
plot(radius1, phi1)
hold
plot(radius2, phi2)

figure(2)
plot(radius1, dphi1dr)
hold
plot(radius2, dphi2dr)


phi0 = 1000, sigma1 = 1, sigma2=.1, R1 = .001, R2 = .025, R3 = .05;
A1=                             -(R1*R2*R3*phi0*sigma2)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
B1= (phi0*(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2))/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
A2=                             -(R1*R2*R3*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);
B2=                                 (R1*R2*phi0*sigma1)/(R1*R2*sigma1 - R1*R3*sigma1 + R1*R3*sigma2 - R2*R3*sigma2);

radius1= [R1:.0005:R2];
phi1= radius1.^(-1)*A1 +B1;
dphi1dr=-radius1.^(-2)*A1;
 
radius2= [R2:.0005:R3];
phi2= radius2.^(-1)*A2 +B2;
dphi2dr=-radius2.^(-2)*A2;

figure(1)
plot(radius1, phi1)
plot(radius2, phi2)
xlabel('radius [m]')
ylabel('potential')

figure(2)
plot(radius1, dphi1dr)
plot(radius2, dphi2dr)
xlabel('radius [m]')
ylabel('Efield')
