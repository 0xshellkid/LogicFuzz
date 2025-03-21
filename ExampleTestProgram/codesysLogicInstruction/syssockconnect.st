PROGRAM PLC_PRG
VAR_INPUT    
diSocket: DINT;    
pSockAddr: DWORD;    
diSockAddrSize: DINT;
END_VAR

diSocket := 1;
pSockAddr := 2;
diSockAddrSize := 3;
//Execute the SysSockConnect instruction
SysSockConnect(diSocket, 
pSockAddr, diSockAddrSize);

