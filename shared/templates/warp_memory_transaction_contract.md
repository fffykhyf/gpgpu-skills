# Warp Memory Transaction Contract

## Required Fields

`warp_id`, `pc`, `instruction_id`, `access_type`, `lane_addresses`,
`active_mask`, `byte_mask`, `sector_mask`, `transaction_address`,
`transaction_size`, `coalesced_group_id`, `is_read`, `is_write`, `is_atomic`.

## Rule

No cache, L2, DRAM, or return-path attribution is valid before this transaction
record exists.

