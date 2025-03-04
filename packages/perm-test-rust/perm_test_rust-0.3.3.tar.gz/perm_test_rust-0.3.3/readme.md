# perm test rust
A rust implementation of comparative permutation testing, because python is not that fast

Input example: ` perm_test.test(amount, group_1, group_2) `.

Output of type: `p_value, [tstats of permutations]`.

Can also return a single tstat if called with `perm_test.calc_tstat(group_1, group_2)`.

Is able to run multiple test if used with `perm_test.multitest(amount, group_1, group_2)`, 
though this feature is not faster than iterating over single tests from within python.

Warning: running lots of tests and/or permutations may take a lot of processing power and time.
