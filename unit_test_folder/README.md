# Problem/Examples

## Problem
Define the Problem

Goal: given a sorted SAM file of uniquely mapped reads, remove all PCR duplicates (retain only a single copy of each read).
- PCR-duplicates have the same alignment position and the same UMI. The alignment position includes chromosome, position, and strand. 
    - POS (SAM col 4) refers to the left most start position of the alignment. This can be affected by soft-clipping which is when a portion of the read does not align to the genome. Soft-clipping can only occur on the ends of the read (either 5' or 3'). 
        - Use the CIGAR string to determine if soft-clipping occured. There will be an "S" in the CIGAR string if clipped sequences are present. If there is soft-clipping adjust POS to reflect the actual start of the alignment. 
        - If POS is not adjusted when there is soft-clipping on the 5' end it will cause PCR duplicates to not be identified. 
    - Parse the bitwise FLAG to determine which strand the read mapped to, either (+) or (-). If reads are on different strands they are not PCR duplicates. 
    - UMIs are used to determine if two reads originated from the same molecule of DNA/RNA isolated from our sample. They are used to distinguish between PCR duplicates and from multiple copies of the same transcript that happen to be aligning to the same place on the genome. 


## Test Examples

Total lines per file: 
- input_test.sam : 79 
- output_test.sam: 74

What I am testing in input_test.sam: 
- Is the read unmapped? If so, move on to the next read. 
    - Test: change the bitwise flag to 4
    - output: Not included in the output
- PCR duplicate? 
    - Test_1: 3 lines are exactly the same. 
    - Output_1: only the first read is written to the output file, the duplicates are not in the output file. 

    - Test_2: 2 additional lines are exactly the same except that one has soft-clipping (will test that the soft clipping function is working properly to adjust POS)
    - Output_2: only the first read is written to the output file. 

- Not a PCR duplicate: 
    - Different chromosome (RNAME): 
        - Test: 2 lines are the same except for RNAME.
        - Output: both lines are written to the output file. 
    - Different position (POS): 
        - Test: 2 lines are the same except for POS.
        - Output: both lines are written to the output file. 
    - Different strands (FLAG): 
        - Test: 2 lines are the same except for which strand the read aligned to. One bitwise flag will be 16 (mapped to - strand) and the other line will have a bitwise flag of 0 (mapped to + strand). 
        - Output: both lines are written to the output file. 
    - Different UMIs (QNAME) or unknown UMI: 
        - Test: 2 lines that are identical except for the known UMIs and another line that has an unknown UMI. 
        - Output: 2 lines with known UMIs are in the output file. The line with the unknown UMI is skipped and not included in the output file. 
