.text
.global vecadd
vecadd:
  lw r4, 0(r1)      # A[lane]
  lw r5, 0(r2)      # B[lane]
  add r6, r4, r5
  sw r6, 0(r3)      # C[lane]
  beq r0, r0, done
done:
  beq r0, r0, done

.data
A:
  .word 1, 2, 3, 4
B:
  .word 10, 20, 30, 40
C:
  .word 0, 0, 0, 0
