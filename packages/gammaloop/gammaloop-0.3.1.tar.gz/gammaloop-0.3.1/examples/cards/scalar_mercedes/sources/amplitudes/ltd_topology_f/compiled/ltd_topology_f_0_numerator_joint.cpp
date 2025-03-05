#include <iostream>
#include <complex>
#include <cmath>

extern "C" void drop_buffer_complex(std::complex<double> *buffer)
{
	delete[] buffer;
}

extern "C" void drop_buffer_double(double *buffer)
{
	delete[] buffer;
}

extern "C" std::complex<double> *ltd_topology_f_0_numerator_joint_create_buffer_complex()
{
	return new std::complex<double>[51];
}

extern "C" double *ltd_topology_f_0_numerator_joint_create_buffer_double()
{
	return new double[51];
}


template<typename T>
void ltd_topology_f_0_numerator_joint(T* params, T* Z, T* out) {
	T Z0, Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9, Z10, Z11, Z12, Z13, Z14, Z15, Z16, Z17, Z18, Z19, Z20, Z21, Z22, Z23, Z24, Z25, Z26, Z27, Z28, Z29, Z30, Z31, Z32, Z33, Z34, Z35, Z36, Z37, Z38, Z39, Z40, Z41, Z42, Z43, Z44, Z45, Z46, Z47, Z48, Z49, Z50;
	Z0 = params[0];
	Z1 = params[1];
	Z2 = params[2];
	Z3 = params[3];
	Z4 = params[4];
	Z5 = params[5];
	Z6 = params[6];
	Z7 = params[7];
	Z8 = params[8];
	Z9 = params[9];
	Z10 = params[10];
	Z11 = params[11];
	Z12 = params[12];
	Z13 = params[13];
	Z14 = params[14];
	Z15 = params[15];
	Z16 = params[16];
	Z17 = params[17];
	Z18 = params[18];
	Z19 = params[19];
	Z20 = params[20];
	Z21 = params[21];
	Z22 = params[22];
	Z23 = params[23];
	Z24 = params[24];
	Z25 = params[25];
	Z26 = params[26];
	Z27 = params[27];
	Z28 = params[28];
	Z29 = params[29];
	Z30 = params[30];
	Z31 = params[31];
	Z32 = params[32];
	Z33 = params[33];
	Z34 = params[34];
	Z35 = params[35];
	Z36 = params[36];
	Z37 = params[37];
	Z38 = params[38];
	Z39 = params[39];
	Z40 = params[40];
	Z41 = params[41];
	Z42 = params[42];
	Z43 = params[43];
	Z44 = params[44];
	Z45 = params[45];
	Z46 = params[46];
	Z47 = params[47];
	Z48 = params[48];
	Z49 = params[49];
	Z50 = Z38*Z38*Z38*Z38*Z38;
	out[0] = Z50;
	return;
}

extern "C" {
	void ltd_topology_f_0_numerator_joint_double(double *params, double *buffer, double *out) {
		ltd_topology_f_0_numerator_joint(params, buffer, out);
		return;
	}
}

extern "C" {
	void ltd_topology_f_0_numerator_joint_complex(std::complex<double> *params, std::complex<double> *buffer,  std::complex<double> *out) {
		ltd_topology_f_0_numerator_joint(params, buffer, out);
		return;
	}
}
