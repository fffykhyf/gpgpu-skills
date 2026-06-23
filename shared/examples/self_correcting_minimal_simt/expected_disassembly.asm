.text
vecadd:
  lw r4, 0(r1)
  lw r5, 0(r2)
  add r6, r4, r5
  sw r6, 0(r3)
  beq r0, r0, done
done:
  beq r0, r0, done
