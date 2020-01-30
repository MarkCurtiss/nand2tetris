// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

//    result = 0;
//    while (i = 0 ; i < R1; i++) {
//        result = result + R0   ;
//    }


    @i          // i = 0
    M=0
    @result     // result = 0
	M=0

    (LOOP)
    @i          // if i - R1 == 0...
    D=M
    @R1
    D=D-M
    @END
    D;JEQ       // ...then stop looping


    @R0         // result += R0
    D=M
    @result
    M=M+D

    @i          // i = i+1
    M=M+1

    @LOOP       // next iteration of loop
    0;JMP
    (END)

    @result    //R2 == result
    D=M
    @R2
    M=D
