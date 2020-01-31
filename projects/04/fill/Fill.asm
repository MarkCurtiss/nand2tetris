// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

	//Screen The Hack computer includes a black-and-white screen organized as 256 rows of 512 pixels per row.
	//The screen’s contents are represented by an 8K memory map that starts at RAM address 16384 (0x4000).
	//Each row in the physical screen, starting at the screen’s top left corner, is represented in the RAM by 32 consecutive 16-bit words.
	//Thus the pixel at row r from the top and column c from the left is mapped on the c%16 bit (counting from LSB to MSB) of the word located at RAM[16384 + r · 32 + c/16].
	//To write or read a pixel of the physical screen, one reads or writes the corresponding bit in the RAM-resident memory map (1 = black, 0 = white).


	@SCREEN		//currentpixel = screen
	D=A
	@CURRENTPIXEL
	M=D

	(LOOP)
	@KBD    // if keypress then FILL else CLEAR
	D=M	// poll keyboard
	@FILL
	D;JGT	// keypress detected, fill
	@CLEAR
	0;JMP   // else, clear screen

	(FILL)
	@CURRENTPIXEL
	D=M



	@CURRENTPIXEL	//currentpixel++
	A=A+1

	@LOOP
	0;JMP

	(CLEAR)  // while (i = 0; i < 256*512; i++) {
	@i
	M=0
	D=M
	@131072  // i < 256*512
	D=D-A
	@LOOP
	D;JEQ   // go to loop
	@i
	D=M
	@SCREEN  // screen[i] = 0;
	A=D+A
	M=0

	@CLEAR
	0;JMP   // continue loop
