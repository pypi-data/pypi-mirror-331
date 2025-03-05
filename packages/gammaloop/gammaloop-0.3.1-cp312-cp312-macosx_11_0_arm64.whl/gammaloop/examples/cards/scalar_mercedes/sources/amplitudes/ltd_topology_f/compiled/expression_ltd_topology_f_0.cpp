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

extern "C" std::complex<double> *joint_create_buffer_complex()
{
	return new std::complex<double>[78];
}

extern "C" double *joint_create_buffer_double()
{
	return new double[78];
}


template<typename T>
void joint(T* params, T* Z, T* out) {
	T Z0, Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8, Z9, Z10, Z11, Z12, Z13, Z14, Z15, Z16, Z17, Z18, Z19, Z20, Z21, Z22, Z23, Z24, Z25, Z26, Z27, Z28, Z29, Z30, Z31, Z32, Z33, Z34, Z35, Z36, Z37, Z38, Z39, Z40, Z41, Z42, Z43, Z44, Z45, Z46, Z47, Z48, Z49, Z50, Z51, Z52, Z53, Z54, Z55, Z56, Z57, Z58, Z59, Z60, Z61, Z62, Z63, Z64, Z65, Z66, Z67, Z68, Z69, Z70, Z71, Z72, Z73, Z74, Z75, Z76, Z77;
	Z0 = params[0];
	Z1 = params[1];
	Z2 = params[2];
	Z3 = params[3];
	Z4 = params[4];
	Z5 = params[5];
	Z6 = params[6];
	Z7 = params[7];
	Z8 = params[8];
	Z9 = -1;
	Z10 = Z3+Z8;
	Z11 = Z4+Z7;
	Z12 = Z2+Z5;
	Z13 = Z0+Z12;
	Z13 = pow(Z13, -1);
	Z14 = Z0+Z2+Z6+Z11;
	Z14 = pow(Z14, -1);
	Z15 = Z13*Z14;
	Z16 = Z6+Z7+Z8;
	Z16 = pow(Z16, -1);
	Z17 = Z2+Z3+Z6;
	Z17 = pow(Z17, -1);
	Z18 = Z16*Z17*Z15;
	Z19 = Z2+Z7+Z10;
	Z19 = pow(Z19, -1);
	Z20 = Z19*Z16;
	Z21 = Z19*Z17;
	Z22 = Z0+Z3+Z11;
	Z22 = pow(Z22, -1);
	Z23 = Z0+Z5+Z7+Z10;
	Z23 = pow(Z23, -1);
	Z24 = Z22*Z23*Z20;
	Z25 = Z22*Z23*Z16;
	Z26 = Z22*Z14*Z16;
	Z25 = Z25+Z26;
	Z25 = Z25*Z13;
	Z26 = Z4+Z5+Z8;
	Z26 = pow(Z26, -1);
	Z27 = Z9*Z0;
	Z28 = Z4+Z6+Z27+Z10;
	Z28 = pow(Z28, -1);
	Z29 = Z28*Z16;
	Z30 = Z2+Z4+Z8+Z27;
	Z30 = pow(Z30, -1);
	Z31 = Z26*Z30*Z29;
	Z32 = Z26*Z29;
	Z33 = Z17*Z29;
	Z32 = Z32+Z33;
	Z32 = Z32*Z13;
	Z33 = Z23*Z20;
	Z34 = Z30*Z20;
	Z33 = Z33+Z34;
	Z33 = Z33*Z26;
	Z34 = Z13*Z26*Z23*Z16;
	Z12 = Z27+Z12;
	Z12 = pow(Z12, -1);
	Z35 = Z3+Z5+Z6+Z27;
	Z35 = pow(Z35, -1);
	Z36 = Z5+Z6+Z11;
	Z36 = pow(Z36, -1);
	Z37 = Z16*Z36;
	Z36 = Z26*Z36;
	Z38 = Z12*Z35*Z37;
	Z39 = Z14*Z37;
	Z40 = Z35*Z37;
	Z39 = Z39+Z40;
	Z39 = Z39*Z17;
	Z40 = Z22*Z20;
	Z41 = Z22*Z37;
	Z40 = Z40+Z41;
	Z40 = Z40*Z12;
	Z41 = Z14*Z22*Z37;
	Z42 = Z30*Z29;
	Z43 = Z35*Z29;
	Z42 = Z42+Z43;
	Z42 = Z42*Z12;
	Z29 = Z17*Z35*Z29;
	Z43 = Z30*Z12*Z20;
	Z44 = Z0+Z3+Z5+Z6;
	Z44 = pow(Z44, -1);
	Z45 = Z44*Z23;
	Z23 = Z19*Z23;
	Z46 = Z45+Z23;
	Z46 = Z46*Z22*Z17;
	Z47 = Z13*Z22*Z45;
	Z48 = Z19*Z30;
	Z23 = Z48+Z23;
	Z23 = Z23*Z26;
	Z48 = Z26*Z45;
	Z23 = Z23+Z48;
	Z23 = Z23*Z17;
	Z45 = Z13*Z26*Z45;
	Z48 = Z22*Z12*Z21;
	Z49 = Z30*Z12*Z21;
	Z50 = Z3+Z27+Z11;
	Z50 = pow(Z50, -1);
	Z28 = Z28*Z50;
	Z51 = Z26*Z30*Z28;
	Z52 = Z26*Z28;
	Z53 = Z17*Z28;
	Z52 = Z52+Z53;
	Z52 = Z52*Z13;
	Z53 = Z30*Z28;
	Z54 = Z35*Z28;
	Z53 = Z53+Z54;
	Z53 = Z53*Z12;
	Z28 = Z17*Z35*Z28;
	Z11 = Z2+Z6+Z27+Z11;
	Z11 = pow(Z11, -1);
	Z54 = Z11*Z12;
	Z55 = Z26*Z30;
	Z55 = Z55+Z36;
	Z55 = Z11*Z55;
	Z56 = Z50*Z55;
	Z57 = Z13*Z50*Z36;
	Z58 = Z44*Z36;
	Z55 = Z58+Z55;
	Z55 = Z55*Z17;
	Z58 = Z13*Z44*Z36;
	Z59 = Z30*Z50*Z54;
	Z30 = Z17*Z30*Z54;
	Z60 = Z0+Z2+Z4+Z8;
	Z60 = pow(Z60, -1);
	Z61 = Z17*Z60*Z15;
	Z15 = Z22*Z60*Z15;
	Z62 = Z12*Z35*Z36;
	Z63 = Z35*Z36;
	Z64 = Z60*Z26;
	Z64 = Z64+Z36;
	Z14 = Z14*Z64;
	Z63 = Z63+Z14;
	Z63 = Z63*Z17;
	Z36 = Z22*Z12*Z36;
	Z14 = Z22*Z14;
	Z64 = Z0+Z4+Z6+Z10;
	Z64 = pow(Z64, -1);
	Z65 = Z64*Z16;
	Z22 = Z22*Z64;
	Z64 = Z17*Z44*Z22;
	Z66 = Z60*Z22;
	Z67 = Z44*Z22;
	Z66 = Z66+Z67;
	Z66 = Z66*Z13;
	Z67 = Z26*Z22;
	Z68 = Z17*Z22;
	Z67 = Z67+Z68;
	Z67 = Z67*Z12;
	Z22 = Z26*Z60*Z22;
	Z68 = Z13*Z60*Z21;
	Z21 = Z13*Z50*Z21;
	Z10 = Z5+Z7+Z27+Z10;
	Z10 = pow(Z10, -1);
	Z27 = Z10*Z35;
	Z35 = Z26*Z12*Z27;
	Z69 = Z60*Z19;
	Z19 = Z19*Z10;
	Z69 = Z69+Z19;
	Z69 = Z69*Z26;
	Z70 = Z26*Z27;
	Z69 = Z69+Z70;
	Z69 = Z69*Z17;
	Z70 = Z12*Z50*Z27;
	Z19 = Z27+Z19;
	Z19 = Z19*Z17*Z50;
	Z27 = Z13*Z60*Z20;
	Z71 = Z17*Z44*Z65;
	Z72 = Z60*Z65;
	Z73 = Z44*Z65;
	Z72 = Z72+Z73;
	Z72 = Z72*Z13;
	Z73 = Z50*Z11*Z37;
	Z74 = Z50*Z20;
	Z75 = Z50*Z37;
	Z74 = Z74+Z75;
	Z74 = Z74*Z13;
	Z75 = Z44*Z37;
	Z76 = Z11*Z37;
	Z75 = Z75+Z76;
	Z75 = Z75*Z17;
	Z13 = Z13*Z44*Z37;
	Z37 = Z26*Z10*Z16*Z12;
	Z44 = Z60*Z20;
	Z76 = Z10*Z20;
	Z44 = Z44+Z76;
	Z44 = Z44*Z26;
	Z76 = Z26*Z65;
	Z77 = Z17*Z65;
	Z76 = Z76+Z77;
	Z76 = Z76*Z12;
	Z26 = Z26*Z60*Z65;
	Z11 = Z11*Z16*Z50;
	Z60 = Z10*Z16*Z50;
	Z11 = Z11+Z60;
	Z11 = Z11*Z12;
	Z10 = Z50*Z10*Z20;
	Z12 = Z16*Z17*Z54;
	out[0] = Z18;
	out[1] = Z24;
	out[2] = Z25;
	out[3] = Z31;
	out[4] = Z32;
	out[5] = Z33;
	out[6] = Z34;
	out[7] = Z38;
	out[8] = Z39;
	out[9] = Z40;
	out[10] = Z41;
	out[11] = Z42;
	out[12] = Z29;
	out[13] = Z43;
	out[14] = Z46;
	out[15] = Z47;
	out[16] = Z23;
	out[17] = Z45;
	out[18] = Z48;
	out[19] = Z49;
	out[20] = Z51;
	out[21] = Z52;
	out[22] = Z53;
	out[23] = Z28;
	out[24] = Z56;
	out[25] = Z57;
	out[26] = Z55;
	out[27] = Z58;
	out[28] = Z59;
	out[29] = Z30;
	out[30] = Z61;
	out[31] = Z15;
	out[32] = Z62;
	out[33] = Z63;
	out[34] = Z36;
	out[35] = Z14;
	out[36] = Z64;
	out[37] = Z66;
	out[38] = Z67;
	out[39] = Z22;
	out[40] = Z68;
	out[41] = Z21;
	out[42] = Z35;
	out[43] = Z69;
	out[44] = Z70;
	out[45] = Z19;
	out[46] = Z27;
	out[47] = Z71;
	out[48] = Z72;
	out[49] = Z73;
	out[50] = Z74;
	out[51] = Z75;
	out[52] = Z13;
	out[53] = Z37;
	out[54] = Z44;
	out[55] = Z76;
	out[56] = Z26;
	out[57] = Z11;
	out[58] = Z10;
	out[59] = Z12;
	return;
}

extern "C" {
	void joint_double(double *params, double *buffer, double *out) {
		joint(params, buffer, out);
		return;
	}
}

extern "C" {
	void joint_complex(std::complex<double> *params, std::complex<double> *buffer,  std::complex<double> *out) {
		joint(params, buffer, out);
		return;
	}
}
