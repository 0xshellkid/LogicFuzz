PROGRAM PLC_PRG
VAR
    Dest : DINT;     
    Src : DINT;      
    udiCount : DINT; 
END_VAR

Dest := 12345678;  
Src := 87654321;   
udiCount := 4;     

SysMemMove( Dest, Src, udiCount );
