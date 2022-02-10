import numpy as np
import pandas as pd
import os
import sys

class MipsSimulator():
    
    def SimulateFile(self,file_nm,strt_addr):
        data=self.read_input_data(file_nm)
        break_index,break_index_value=self.break_index_value(data)
        instructions_data=data[0][0:break_index+1]
        register_values=data[break_index+1:][0]
        register_decimal_values = [self.convert_complement_on_two_into_decimal(i) for i in register_values]
        m=[]
        for i in instructions_data:
            m.append(self.categorydivision(i,strt_addr))
            strt_addr=strt_addr+4
        n=[]
        for i in register_values:
            n.append([i,str(strt_addr),str(self.convert_complement_on_two_into_decimal(i))])
            strt_addr=strt_addr+4
        disassembly=m+n
        output_txt=pd.DataFrame(disassembly)
        np.savetxt('disassembly.txt', output_txt.values, fmt='%s', delimiter="\t")
        Registers = [0 for i in range(32)]
        self.run_simlation(break_index,disassembly,Registers)        
    
    def read_input_data(self,file_nm):
        data = pd.read_csv(file_nm, sep=" ", header=None)
        return data
    def convert_complement_on_two_into_decimal(self,bits):
        return -int(bits[0]) << len(bits) | int(bits, 2)
    def break_index_value(self,data):
        break_index=0
        for i in data[0]:
            if i[0:6]=='000110':
                break_index_value=i 
                return break_index,break_index_value
            else:
                break_index=break_index+1 

    def categorydivision(self,bits,num):
        if bits[0:3]=='000':
            if bits[3:6]=='000':
                return [str(bits),str(num),str("J"+" #"+str(int(bits[6:],2)<<2))]
            if bits[3:6]=='001':
                return [str(bits),str(num),str("BEQ R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:],2)<<2))]
            if bits[3:6]=='010':
                return [str(bits),str(num),str("BNE R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:],2)<<2))]
            if bits[3:6]=='011':
                return [str(bits),str(num),str("BGTZ R"+str(int(bits[6:11],2))+","+" #"+str(int(bits[16:],2)<<2))]
            if bits[3:6]=='100':
                return [str(bits),str(num),str("SW R"+str(int(bits[11:16],2))+", "+str(int(bits[16:],2))+"(R"+str(int(bits[6:11],2))+")")]
            if bits[3:6]=='101':
                return [str(bits),str(num),str("LW R"+str(int(bits[11:16],2))+", "+str(int(bits[16:],2))+"(R"+str(int(bits[6:11],2))+")")]  
            if bits[3:6]=='110':
                return [str(bits),str(num),"BREAK"]
        if bits[0:3]=='001':
            if bits[3:6]=='000':
                return [str(bits),str(num),str("ADD R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", R"+str(int(bits[16:21],2)))]
            if bits[3:6]=='001':
                return [str(bits),str(num),str("SUB R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", R"+str(int(bits[16:21],2)))]
            if bits[3:6]=='010':
                return [str(bits),str(num),str("AND R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", R"+str(int(bits[16:21],2)))]
            if bits[3:6]=='011':
                return [str(bits),str(num),str("OR R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", R"+str(int(bits[16:21],2)))]
            if bits[3:6]=='100':
                return [str(bits),str(num),str("SRL R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:21],2)))]
            if bits[3:6]=='101':
                return [str(bits),str(num),str("SRA R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:21],2)))]
            if bits[3:6]=='110':
                return [str(bits),str(num),str("MUL R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", R"+str(int(bits[16:21],2)))]        
        if bits[0:3]=='010':
            if bits[3:6]=='000':
                return [str(bits),str(num),str("ADDI R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(self.convert_complement_on_two_into_decimal(bits[16:])))]
            if bits[3:6]=='001':
                return [str(bits),str(num),str("ANDI R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:],2)))]
            if bits[3:6]=='010':
                return [str(bits),str(num),str("ORI R"+str(int(bits[6:11],2))+", R"+str(int(bits[11:16],2))+", #"+str(int(bits[16:],2)))]

    def getregdatas(self,disassembly,break_index):
        reg_datas=[]
        strt_pt=int(disassembly[break_index+1][1])
        end_pt=int(disassembly[len(disassembly)-1][1])
        while(strt_pt<end_pt):
            reg_dts=[]
            reg_dts.append(str(strt_pt)+":")
            for i in range(8):
                if(break_index+1+i)<(len(disassembly)-1):
                    reg_dts.append(str(pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str(strt_pt)][2].values[0]))
                strt_pt=int(strt_pt)+4
            reg_datas.append(reg_dts)
        return reg_datas
    def srl(self,val, n):
        return val>>n if val >= 0 else (val+0x100000000)>>n
    def sra(self,x,k):
        if (x<0):
            x = -((-x)>>k)
        else:
            x = x>>k
        return x
    def Registervalueupdates(self,disassembly,k,Registers,break_index):
        if str(disassembly[k][2])[0:4]=='ADD ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]+Registers[int(disassembly[k][0][16:21],2)]
            return Registers,disassembly,k+1     
        if str(disassembly[k][2])[0:4]=='SUB ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]-Registers[int(disassembly[k][0][16:21],2)]
            return Registers,disassembly,k+1     
        if str(disassembly[k][2])[0:4]=='MUL ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]*Registers[int(disassembly[k][0][16:21],2)]
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:4]=='AND ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]&Registers[int(disassembly[k][0][16:21],2)]
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:3]=='OR ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]|Registers[int(disassembly[k][0][16:21],2)]
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:4]=='SRL ':
            Registers[int(disassembly[k][0][6:11],2)]=self.srl(Registers[int(disassembly[k][0][11:16],2)],int(disassembly[k][0][16:21],2))
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:4]=='SRA ':
            Registers[int(disassembly[k][0][6:11],2)]=self.sra(Registers[int(disassembly[k][0][11:16],2)],int(disassembly[k][0][16:21],2))
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:5]=='ADDI ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]+int(disassembly[k][0][16:32],2)
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:5]=='ANDI ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]&int(disassembly[k][0][16:32],2)
            return Registers,disassembly,k+1 
        if str(disassembly[k][2])[0:4]=='ORI ':
            Registers[int(disassembly[k][0][6:11],2)]=Registers[int(disassembly[k][0][11:16],2)]|int(disassembly[k][0][16:32],2)
            return Registers,disassembly,k+1
        if str(disassembly[k][2])[0:2]=='J ':
            k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str(int(disassembly[k][0][6:],2)<<2)][2].index[0]
            return Registers,disassembly,k
        if str(disassembly[k][2])[0:5]=='BREAK':
            k=break_index+1
            return Registers,disassembly,k 
        if str(disassembly[k][2])[0:4]=='BEQ ':
            if Registers[int(disassembly[k][0][6:11],2)]==Registers[int(disassembly[k][0][11:16],2)]:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return Registers,disassembly,k
            else:
                return Registers,disassembly,k+1
        if str(disassembly[k][2])[0:4]=='BNE ':
            if Registers[int(disassembly[k][0][6:11],2)]!=Registers[int(disassembly[k][0][11:16],2)]:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return Registers,disassembly,k
            else:
                return Registers,disassembly,k+1
        if str(disassembly[k][2])[0:5]=='BGTZ ':
            if Registers[int(disassembly[k][0][6:11],2)]>0:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return Registers,disassembly,k
            else:
                return Registers,disassembly,k+1
        if str(disassembly[k][2])[0:3]=='SW ': 
            disassembly[pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2))+Registers[int(disassembly[k][0][6:11],2)])][2].index[0]][2]=Registers[int(disassembly[k][0][11:16],2)]
            return Registers,disassembly,k+1
        if str(disassembly[k][2])[0:3]=='LW ': 
            Registers[int(disassembly[k][0][11:16],2)]=int(disassembly[pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2))+Registers[int(disassembly[k][0][6:11],2)])][2].index[0]][2])
            return Registers,disassembly,k+1    
        return Registers,disassembly,k+1      

    def run_simlation(self,break_index,disassembly,Registers):
        sim=[]
        j=1
        k=0
        while(k<=break_index):
            sim.append('--------------------')
            sim.append('Cycle '+str(j)+":"+str("\t")+str(disassembly[k][1])+str("\t")+str(disassembly[k][2]))
            sim.append('')
            sim.append('Registers')
            Registers,disassembly,k=self.Registervalueupdates(disassembly,k,Registers,break_index)
            reg_datas=self.getregdatas(disassembly,break_index)
            sim.append('R00:\t'+str(Registers[0])+'\t'+str(Registers[1])+'\t'+str(Registers[2])+'\t'+str(Registers[3])+'\t'+str(Registers[4])+'\t'+str(Registers[5])+'\t'+str(Registers[6])+'\t'+str(Registers[7]))
            sim.append('R08:\t'+str(Registers[8])+'\t'+str(Registers[9])+'\t'+str(Registers[10])+'\t'+str(Registers[11])+'\t'+str(Registers[12])+'\t'+str(Registers[13])+'\t'+str(Registers[14])+'\t'+str(Registers[15]))
            sim.append('R16:\t'+str(Registers[16])+'\t'+str(Registers[17])+'\t'+str(Registers[18])+'\t'+str(Registers[19])+'\t'+str(Registers[20])+'\t'+str(Registers[21])+'\t'+str(Registers[22])+'\t'+str(Registers[23]))
            sim.append('R24:\t'+str(Registers[24])+'\t'+str(Registers[25])+'\t'+str(Registers[26])+'\t'+str(Registers[27])+'\t'+str(Registers[28])+'\t'+str(Registers[29])+'\t'+str(Registers[30])+'\t'+str(Registers[31]))
            sim.append('')
            sim.append('Data')                       
            for i in reg_datas:        
                sim.append('\t'.join(i))            
            sim.append('')
            j=j+1
        simulation_txt=pd.DataFrame(sim)
        simulation_txt.drop(simulation_txt.tail(1).index,inplace=True)
        np.savetxt('simulation.txt', simulation_txt.values, fmt='%s', delimiter="\t")

if __name__ == '__main__':
    file_nm=sys.argv[1]
    strt_addr=260
    obj=MipsSimulator()
    obj.SimulateFile(file_nm,strt_addr)      