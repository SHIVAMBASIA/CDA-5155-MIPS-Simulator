import numpy as np
import pandas as pd
import os
import sys
import re

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
        #np.savetxt('disassembly.txt', output_txt.values, fmt='%s', delimiter="\t")
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

   
    def Branch_instructions(self,disassembly,k,Registers,break_index):
        if str(disassembly[k][2])[0:2]=='J ':
            k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str(int(disassembly[k][0][6:],2)<<2)][2].index[0]
            return k
        if str(disassembly[k][2])[0:5]=='BREAK':
            k=break_index+1
            return k 
        if str(disassembly[k][2])[0:4]=='BEQ ':
            if Registers[int(disassembly[k][0][6:11],2)]==Registers[int(disassembly[k][0][11:16],2)]:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return k
            else:
                return k+1
        if str(disassembly[k][2])[0:4]=='BNE ':
            if Registers[int(disassembly[k][0][6:11],2)]!=Registers[int(disassembly[k][0][11:16],2)]:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return k
            else:
                return k+1
        if str(disassembly[k][2])[0:5]=='BGTZ ':
            if Registers[int(disassembly[k][0][6:11],2)]>0:
                k=pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(disassembly[k][0][16:],2)<<2)+int(disassembly[k][1]))][2].index[0]+1
                return k
            else:
                return k+1


    def run_simlation(self,break_index,disassembly,Registers):
        sim=[]
        j=1
        k=0
        Waiting=[]
        Executed=[]
        Buf1=[]
        Buf2=[]
        Buf3=[]
        Buf4=[]
        Buf5=[]
        Buf6=[]
        Buf7=[]
        Buf8=[]
        Buf9=[]
        Buf10=[]

        while(k<=break_index):   
            load_buffer=[]
            if len(Executed)>0:
                Executed.pop(0)

            if len(Waiting)>0 and len(Executed)==0:                     
                if any(item in re.findall("R\d",str(Buf1+Buf2+Buf3+Buf4+Buf5+Buf6+Buf7+Buf8+Buf9+Buf10)) for item in re.findall("R\d",Waiting[0]))==False:     
                    if (str(disassembly[k][2])[0:5]=='BREAK')==True:
                        if (len(Buf1)+len(Buf2)+len(Buf3)+len(Buf4)+len(Buf5)+len(Buf6)+len(Buf7)+len(Buf8)+len(Buf9)+len(Buf10))==0:
                            Executed.append(Waiting.pop(0))
                            k=self.Branch_instructions(disassembly,k,Registers,break_index)
                    else:
                        Executed.append(Waiting.pop(0))
                        k=self.Branch_instructions(disassembly,k,Registers,break_index)                       
                    

            
            if len(Buf10)>0:
                Registers[int(Buf10[0].split(',')[1][2:])]=int(Buf10[0].split(',')[0][0:])
                load_buffer.append(Buf10[0])
                Buf10.pop(0)            
            
            
            
            if len(Buf9)>0:
                if Buf9[0][0:4]=='MUL ':
                    Buf10.append(str(Registers[int(Buf9[0].split(',')[1][2:])]*Registers[int(Buf9[0].split(',')[2][2:])])+', '+Buf9[0].split(',')[0][4:])
                    load_buffer.append(Buf9[0])
                    Buf9.pop(0)
           
            if len(Buf8)>0:
                Registers[int(Buf8[0].split(',')[1][2:])]=int(Buf8[0].split(',')[0][0:])
                load_buffer.append(Buf8[0])
                Buf8.pop(0)

                        
            
            
            if len(Buf7)>0:
                    Buf9.append(Buf7[0])
                    load_buffer.append(Buf7[0])
                    Buf7.pop(0)              
            
            
            
            if len(Buf6)>0:
                Registers[int(Buf6[0].split(',')[1][2:])]=int(Buf6[0].split(',')[0][0:])
                load_buffer.append(Buf6[0])
                Buf6.pop(0)
                


    
           
        
            if len(Buf5)>0:
                if Buf5[0][0:3]=='LW ':
                    Buf8.append(str(disassembly[pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(Buf5[0].split('(')[0][4:].split(',')[1][1:]))+Registers[int(Buf5[0].split('(')[1][1:].split(')')[0])])][2].index[0]][2])+', '+Buf5[0].split(',')[0][3:])
                    load_buffer.append(Buf5[0])
                    Buf5.pop(0)
                else:
                    disassembly[pd.DataFrame(disassembly)[pd.DataFrame(disassembly)[1]==str((int(Buf5[0].split('(')[0][4:].split(',')[1][1:]))+Registers[int(Buf5[0].split('(')[1][1:].split(')')[0])])][2].index[0]][2]=Registers[int(Buf5[0].split(',')[0][4:])]
                    load_buffer.append(Buf5[0])
                    Buf5.pop(0)
        
            if len(Buf4)>0:
                    Buf7.append(Buf4[0])
                    Buf4.pop(0)                 
            
            if len(Buf3)>0:
                if Buf3[0][0:4]=='ADD ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]+Registers[int(Buf3[0].split(',')[2][2:])])+', '+Buf3[0].split(',')[0][4:])
                if Buf3[0][0:4]=='SUB ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]-Registers[int(Buf3[0].split(',')[2][2:])])+', '+Buf3[0].split(',')[0][4:])
                if Buf3[0][0:4]=='AND ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]&Registers[int(Buf3[0].split(',')[2][2:])])+', '+Buf3[0].split(',')[0][4:])
                if Buf3[0][0:3]=='OR ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]|Registers[int(Buf3[0].split(',')[2][2:])])+', '+Buf3[0].split(',')[0][3:])
                if Buf3[0][0:4]=='SRL ':
                    Buf6.append(str(self.srl(Registers[int(Buf3[0].split(',')[1][2:])],int(Buf3[0].split('#')[1][0:])))+', '+Buf3[0].split(',')[0][4:])
                if Buf3[0][0:4]=='SRA ':
                    Buf6.append(str(self.sra(Registers[int(Buf3[0].split(',')[1][2:])],int(Buf3[0].split('#')[1][0:]))-1)+', '+Buf3[0].split(',')[0][4:])
                if Buf3[0][0:5]=='ADDI ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]+int(Buf3[0].split('#')[1][0:]))+', '+Buf3[0].split(',')[0][5:])
                if Buf3[0][0:5]=='ANDI ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]&int(Buf3[0].split('#')[1][0:]))+', '+Buf3[0].split(',')[0][5:])
                if Buf3[0][0:3]=='ORI ':
                    Buf6.append(str(Registers[int(Buf3[0].split(',')[1][2:])]|int(Buf3[0].split('#')[1][0:]))+', '+Buf3[0].split(',')[0][4:])         
                Buf3.pop(0)     
                
            if len(Buf2)>0:
                if Buf2[0][0:3] in('SW ','LW '): 
                    Buf5.append(Buf2[0])
                    Buf2.pop(0)           
            
            fm=0
            for i in range(len(Buf1)):
                if (Buf1[fm][0:4] in('ADD ','SUB ','AND ','SRL ','SRA ','ORI ') or Buf1[fm][0:3]==('OR ') or Buf1[fm][0:5] in('ADDI ','ANDI ')) and (len(Buf3)+len(Buf6))<2 and any(item in re.findall("R\d",str(Buf1[:fm]+Buf2+Buf3+Buf4+Buf6+Buf7+Buf8+Buf9+Buf10+load_buffer)) for item in re.findall("R\d",Buf1[fm]))==False or(j==2 and len(Buf3)==1):                    
                    Buf3.append(Buf1.pop(fm))
                elif Buf1[fm][0:4] ==('MUL ') and len(Buf4)<2 and any(item in re.findall("R\d",str(Buf1[:fm]+Buf2+Buf3+Buf4+Buf5+Buf6+Buf7+Buf8+Buf9+Buf10+load_buffer)) for item in re.findall("R\d",Buf1[fm]))==False:                    
                    Buf4.append(Buf1.pop(fm))
                elif Buf1[fm][0:3] in('LW ','SW ') and len(Buf2)<2 and any(item in re.findall("R\d",str(Buf1[:fm]+Buf3+Buf4+Buf5+Buf6+Buf7+Buf8+Buf9+Buf10+load_buffer)) for item in re.findall("R\d",Buf1[fm]))==False and (len(Buf3)+len(Buf4)+len(Buf5)+len(Buf6)+len(Buf7)+len(Buf8)+len(Buf9)+len(Buf10))==0 :                    
                    Buf2.append(Buf1.pop(fm))
                else:# Buf1[fm][0:3] in('LW ','SW ') and len(Buf2)<2 and fm<len(Buf1)-1 and any(item in re.findall("R\d",str(Buf1[:fm]+Buf3+Buf4+Buf5+Buf6+Buf7+Buf8+Buf9+Buf10+load_buffer)) for item in re.findall("R\d",Buf1[fm]))==True:                    
                    fm=fm+1




                    
            
            
            if len(Waiting)==0 and len(Executed)==0: 
                for i in range(4):
                    if (str(disassembly[k][2])[0:5]=='BGTZ ') or (str(disassembly[k][2])[0:4]=='BEQ ') or (str(disassembly[k][2])[0:4]=='BNE ') or (str(disassembly[k][2])[0:2]=='J ') or (str(disassembly[k][2])[0:5]=='BREAK'):
                        if any(item in re.findall("R\d",str(Buf1+Buf2+Buf3+Buf4+Buf5+Buf6+Buf7+Buf8+Buf9+Buf10)) for item in re.findall("R\d",str(disassembly[k][2]))) or((str(disassembly[k][2])[0:5]=='BREAK1')==True and (len(Buf1)+len(Buf2)+len(Buf3)+len(Buf4)+len(Buf5)+len(Buf6)+len(Buf7)+len(Buf8)+len(Buf9)+len(Buf10))!=0):
                            Waiting.append(str(disassembly[k][2]))
                        else:
                            Executed.append(str(disassembly[k][2]))
                            k=self.Branch_instructions(disassembly,k,Registers,break_index)
                        break
                    else:
                        Buf1.append(str(disassembly[k][2]))
                        k=k+1

            sim.append('--------------------')
            sim.append('Cycle '+str(j)+":")
            sim.append('')
            sim.append('IF:')
            if len(Waiting)>0:
                sim.append(str("\t")+"Waiting: "+('['+str(Waiting[0])+']'))
            else:
                sim.append(str("\t")+"Waiting:")
            if len(Executed)>0:
                sim.append(str("\t")+"Executed: "+('['+str(Executed[0])+']'))
            else:
                sim.append(str("\t")+"Executed:")
            sim.append('Buf1:')
            if len(Buf1)>0:
                sim.append(str("\t")+"Entry 0: "+('['+str(Buf1[0])+']'))
            else:
                sim.append(str("\t")+"Entry 0:")
            if len(Buf1)>1:
                sim.append(str("\t")+"Entry 1: "+('['+str(Buf1[1])+']'))
            else:
                sim.append(str("\t")+"Entry 1:")                
            if len(Buf1)>2:
                sim.append(str("\t")+"Entry 2: "+('['+str(Buf1[2])+']'))
            else:
                sim.append(str("\t")+"Entry 2:")
            if len(Buf1)>3:
                sim.append(str("\t")+"Entry 3: "+('['+str(Buf1[3])+']'))
            else:
                sim.append(str("\t")+"Entry 3:")
            if len(Buf1)>4:
                sim.append(str("\t")+"Entry 4: "+('['+str(Buf1[4])+']'))
            else:
                sim.append(str("\t")+"Entry 4:")
            if len(Buf1)>5:
                sim.append(str("\t")+"Entry 5: "+('['+str(Buf1[5])+']'))
            else:
                sim.append(str("\t")+"Entry 5:")                
            if len(Buf1)>6:
                sim.append(str("\t")+"Entry 6: "+('['+str(Buf1[6])+']'))
            else:
                sim.append(str("\t")+"Entry 6:")
            if len(Buf1)>7:
                sim.append(str("\t")+"Entry 7: "+('['+str(Buf1[7])+']'))
            else:
                sim.append(str("\t")+"Entry 7:")                
            sim.append('Buf2:')
            if len(Buf2)>0:
                sim.append(str("\t")+"Entry 0: "+('['+str(Buf2[0])+']'))
            else:
                sim.append(str("\t")+"Entry 0:")
            if len(Buf2)>1:
                sim.append(str("\t")+"Entry 1: "+('['+str(Buf2[1])+']'))
            else:
                sim.append(str("\t")+"Entry 1:")            
            sim.append('Buf3:')
            if len(Buf3)>0:
                sim.append(str("\t")+"Entry 0: "+('['+str(Buf3[0])+']'))
            else:
                sim.append(str("\t")+"Entry 0:")
            if len(Buf3)>1:
                sim.append(str("\t")+"Entry 1: "+('['+str(Buf3[1])+']'))
            else:
                sim.append(str("\t")+"Entry 1:")             
            sim.append('Buf4:')
            if len(Buf4)>0:
                sim.append(str("\t")+"Entry 0: "+('['+str(Buf4[0])+']'))
            else:
                sim.append(str("\t")+"Entry 0:")
            if len(Buf4)>1:
                sim.append(str("\t")+"Entry 1: "+('['+str(Buf4[1])+']'))
            else:
                sim.append(str("\t")+"Entry 1:")            
            if len(Buf5)>0:
                sim.append('Buf5: '+('['+str(Buf5[0])+']'))
            else:
                sim.append('Buf5:')
            if len(Buf6)>0:
                sim.append('Buf6: '+('['+str(Buf6[0])+']'))
            else:
                sim.append('Buf6:')
            if len(Buf7)>0:
                sim.append('Buf7: '+('['+str(Buf7[0])+']'))
            else:
                sim.append('Buf7:')
            if len(Buf8)>0:
                sim.append('Buf8: '+('['+str(Buf8[0])+']'))
            else:
                sim.append('Buf8:')
            if len(Buf9)>0:
                sim.append('Buf9: '+('['+str(Buf9[0])+']'))
            else:
                sim.append('Buf9:')
            if len(Buf10)>0:
                sim.append('Buf10: '+('['+str(Buf10[0])+']'))
            else:
                sim.append('Buf10:')
            sim.append('')
            sim.append('Registers')
            reg_datas=self.getregdatas(disassembly,break_index)
            sim.append('R00:\t'+str(Registers[0])+'\t'+str(Registers[1])+'\t'+str(Registers[2])+'\t'+str(Registers[3])+'\t'+str(Registers[4])+'\t'+str(Registers[5])+'\t'+str(Registers[6])+'\t'+str(Registers[7]))
            sim.append('R08:\t'+str(Registers[8])+'\t'+str(Registers[9])+'\t'+str(Registers[10])+'\t'+str(Registers[11])+'\t'+str(Registers[12])+'\t'+str(Registers[13])+'\t'+str(Registers[14])+'\t'+str(Registers[15]))
            sim.append('R16:\t'+str(Registers[16])+'\t'+str(Registers[17])+'\t'+str(Registers[18])+'\t'+str(Registers[19])+'\t'+str(Registers[20])+'\t'+str(Registers[21])+'\t'+str(Registers[22])+'\t'+str(Registers[23]))
            sim.append('R24:\t'+str(Registers[24])+'\t'+str(Registers[25])+'\t'+str(Registers[26])+'\t'+str(Registers[27])+'\t'+str(Registers[28])+'\t'+str(Registers[29])+'\t'+str(Registers[30])+'\t'+str(Registers[31]))
            sim.append('')
            sim.append('Data')                       
            for i in reg_datas:        
                sim.append('\t'.join(i))            
            j=j+1

        simulation_txt=pd.DataFrame(sim)
        np.savetxt('simulation.txt', simulation_txt.values, fmt='%s', delimiter="\t")

if __name__ == '__main__':
    file_nm=sys.argv[1]
    strt_addr=260
    obj=MipsSimulator()
    obj.SimulateFile(file_nm,strt_addr)      