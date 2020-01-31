// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

	@SCREEN		//currentpixel = screen
	D=A
	@CURRENTPIXEL
	M=D

	(LOOP)
	@KBD    // if keypress then FILL else CLEAR
	D=M 	// poll keyboard
	@FILL
	D;JGT	// keypress detected, fill
	@CLEAR
	0;JMP   // else, clear screen

	(FILL)
    @CURRENTPIXEL   //if currentpixel = screensize == 0
    D=M
    @KBD
    D=D-A

    @LOOP           //resume input loop
    D;JEQ

	@CURRENTPIXEL   //otherwise, set the current pixel
    A=M
    M=-1
    D=A
    @CURRENTPIXEL
    M=D+1            //set currentpixel to point to the next pixel

	@LOOP
	0;JMP

	(CLEAR)
    @CURRENTPIXEL   // if currentpixel <= screen, then exit
    D=M
    @SCREEN
    D=D-A
    @LOOP
    D;JLT

	@CURRENTPIXEL
    A=M
    M=0
    D=A
    @CURRENTPIXEL
    M=D-1

    @LOOP
    0;JMP
