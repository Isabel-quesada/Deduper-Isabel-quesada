#!/usr/bin/env python

'''Reference Based PCR Duplicate Removal tool. Given a SAM file of uniquely
mapped reads, remove all PCR duplicates (retain only a single copy of each
read).'''

import argparse
import re


def get_args(): 
    parser = argparse.ArgumentParser(description="PCR Duplicate Removal tool. Assumes the input SAM file is sorted.")
    parser.add_argument("-f", "--file", help="designates absolute file path to sorted sam file", type=str, required=True)
    parser.add_argument("-o", "--outfile", help="designates absolute file path to filtered sam file", type = str, required=True)
    parser.add_argument("-u", "--umi", help="designates file containing the list of known UMIs", type=str, required=True)
    parser.print_help()
    return parser.parse_args()
    
args = get_args()
input_sam = args.file
output_sam = args.outfile
umis = args.umi

def cigar_conversion(cigar, pos, strand):
    '''This function will adjust pos to account for strand and soft-clipping. 
    It will return the adjusted position'''
    x = re.split(r'(\d+)', cigar)
    x = list(filter(None, x))
    if strand=="+": 
        if x[1] == 'S': 
            return(pos - int(x[0]))
        else: 
            return(pos)
    if strand=="-": 
        y = x[0::2]
        new_pos = pos
        for i in y: 
            new_pos+=int(i)
        for count, value in enumerate(x):
            if value=='I':
                index = count-1
                new_pos=new_pos-int(x[index])
            if count==1 and value=='S': 
                new_pos=new_pos-int(x[0])
        return(new_pos)
      
#generate a set of known UMIs
with open(umis, "r") as fh: 
    known_umis = set()
    for i in fh: 
        known_umis.add(i.strip())
    fh.close()


curr_dict = {} #stores current info: curr_dict = {(rname,adj_pos,umi,strand):0}
curr_chr = ""
pcr_duplicate = 0
unknown_umi = 0
uniq_reads = {} #stores the number of unique reads per chromosome. uniq_reads = {chr:number of reads}

#checking for PCR duplicates
with open(input_sam, "r") as file, open(output_sam, "w") as out:
    while True: 
        line = file.readline().strip()
       
        if line == "": 
            # EOF
            break
        if line.startswith('@'): 
            out.write(line + '\n')
            continue
        else: 
            info = line.split()
            rname = info[2] #chromosome
            qname = info[0].split(':') #has umi
            pos = int(info[3])
            flag = int(info[1])
            cigar = ''.join(info[5])
            strand = ""
            umi = qname[7]

            # resets the dictionary when the chromosome number changes
            if rname != curr_chr: 
                curr_chr = rname
                curr_dict = {}
            else: 
                pass

            # check to see if umi is in known_umis set, if not ignore the read and move onto the next one. 
            if umi not in known_umis: 
                unknown_umi+=1
                continue
            else:     
                pass

            # check to see if the read is on the + or - strand
            if((flag & 16) == 16): 
                strand = "-"
            else: 
                strand = "+"
            
            adj_pos = cigar_conversion(cigar,pos,strand)
            key = (rname, adj_pos, umi, strand)

            if key not in curr_dict:
                curr_dict[key]=0
                out.write(line+'\n')
                if rname not in uniq_reads: 
                    uniq_reads[rname]=1
                else: 
                    uniq_reads[rname]+=1
            else: 
                #pcr duplicate
                pcr_duplicate+=1
file.close()
out.close()

with open("statistics.txt","w") as output: 
    output.write(f'Number of unknown UMIs: {unknown_umi}' +'\n' + f'Number of PCR duplicates: {pcr_duplicate}' +'\n' +
                'Number of unique reads per chromosome:' + '\n' + 'Chromosome' + '\t' + 'Number of Reads' +'\n')
    for i in uniq_reads: 
        output.write(f'{i}' + '\t' + f'{uniq_reads[i]}' + '\n')
    output.close()