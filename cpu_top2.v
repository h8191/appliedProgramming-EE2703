`timescale 1ns / 1ps
//Implementation Testbench for DMEM

module top1(
    input clk
    ); //Only input from the outside is clock
	
	reg man_clk,reset;     //mandatory inputs
    reg gate_cpu,gate_dmem; // debugging inputs
    reg [31:0] idata_input, daddr_input;
    wire clk_cpu,clk_dmem;
    wire [31:0]idata_temp, daddr_temp; 

    wire [31:0] iaddr, idata;
    wire [31:0] daddr, drdata, dwdata;
    wire [3:0] we;
    wire [31:0] x31, pc;

    initial begin 
        gate_cpu = 1;
        gate_dmem = 1;
        man_clk = 0;
        reset = 1;
        idata_input = 0;
        daddr_input = 32'hffffffff;
    end

    assign clk_cpu = gate_cpu&man_clk;
    assign clk_dmem = gate_dmem&man_clk;
    assign idata_temp <= idata_input ? idata_input:idata;
    assign daddr_temp <= daddr_input!=32'hffffffff ? daddr_input:daddr;

    CPU c1(
        .clk(clk_cpu),
        .reset(reset),
        .iaddr(iaddr),
        .idata(idata_temp),
        .daddr(daddr),
        .drdata(drdata),
        .dwdata(dwdata),
        .we(we),
        .x31(x31),
        .pc(pc)
    );
	 
	 DMEM d1(
		.clk(clk_dmem),
		.daddr(daddr_temp),
		.dwdata(dwdata),
		.drdata(drdata),
		.we(we)
		);
	 
	 IMEM i1(
		.iaddr(iaddr_temp), 
		.idata(idata)
	);

wire [35:0] VIO_CONTROL;

icon0 instanceB (
	 //Input-output ports controlled by VIO and ILA
	//Control wires used by ICON to control VIO and ILA
	//.CONTROL0(ILA_CONTROL), // INOUT BUS [35:0]
    .CONTROL0(VIO_CONTROL) // INOUT BUS [35:0]
);

vio0 instanceC(
    .CONTROL(VIO_CONTROL), // INOUT BUS [35:0]
	.CLK(clk),
    .SYNC_OUT({man_clk,reset}),
    .SYNC_IN({we,iaddr,idata,daddr,drdata,dwdata,x31,pc})//BUS[224+3:0]
);

/*
ila0 instanceE (
    .CONTROL(ILA_CONTROL), // INOUT BUS [35:0]
    .CLK(clk), // IN
    .TRIG0(outdata)// IN BUS [31:0]	
	
);
*/
endmodule

/*
UCF statement to be added in constraints file-
NET "clk" LOC = "C9"  | IOSTANDARD = LVCMOS33 ;
*/
 