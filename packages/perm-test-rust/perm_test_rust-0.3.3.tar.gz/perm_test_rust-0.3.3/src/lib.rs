use pyo3::prelude::*;
use rand::seq::IndexedRandom;
use rayon::prelude::*;
use std::sync::mpsc;

//use a 2d vector to output a multites
#[pyfunction]
fn multitest(perm: usize, groups_0: Vec<Vec<f64>>, groups_1: Vec<Vec<f64>>) -> PyResult<(Vec<f64>, Vec<Vec<f64>>)> {
    // send an error if the groups don't have the same amount of vectors
    if groups_0.len() != groups_1.len() {
        panic!("Both data groups must contain the same amount of measurement lists")
    }

    //make our output vectors
    let mut t_stats : Vec<Vec<f64>> = Vec::new();
    let mut p_values : Vec<f64> = Vec::new();

    //run a for loop for the amount of data
    for i in 0..groups_0.len() {
        let run_data = test(perm, groups_0[i].clone(), groups_1[i].clone());
        t_stats.push(run_data.1);
        p_values.push(run_data.0);
    }

    Ok((p_values, t_stats))
}


// return p value tstats for the amount of permutations given
#[pyfunction]
fn test(perm: usize, group_0: Vec<f64>, group_1: Vec<f64> ) -> (f64, Vec<f64>) {
    // calculate the initial tstat
    let init_tstat = calc_tstat(group_0.clone(), group_1.clone());

    // assign labels to the different groups
    let mut labels : Vec<bool> = Vec::new();
    for _i in 0..group_0.len(){
        labels.push(false);
    }
    for _i in 0..group_1.len(){
        labels.push(true);
    }
    
    // make a data variable from the different groups
    let data = [group_0, group_1].concat();

    // create a varable to put the randomised t-stats in
    let mut rand_tstat : Vec<f64> = Vec::new();

    //make communication work
    let (tx, rx) = mpsc::channel();
    // make a loop for the length of permutations
    (0..perm).into_par_iter().for_each_with(tx, |tx, _x| tx.send(make_permutation(labels.clone(), data.clone())).unwrap()); 

    for receive in rx{ 
    rand_tstat.push(receive);
            }

    // use calculated and initial tstats to calculate a p value

    let p_value = calc_p_value(init_tstat, rand_tstat.clone());


    (p_value, rand_tstat)
}

//make a function to contain the permutations and their calculations
fn make_permutation(labels: Vec<bool>, data: Vec<f64>) -> f64{

        // create randomised labels
        let mut rng = &mut rand::rng();
        let rand_labels: Vec<bool> = labels.choose_multiple(&mut rng, labels.len()).cloned().collect();
        
        // use these labels to assign data to a group
        let mut group_0 : Vec<f64>= Vec::new();
        let mut group_1 : Vec<f64>= Vec::new();
        for j in 0..rand_labels.len(){
            if rand_labels[j] == true {
                group_1.push(data[j]);
            }
            else {
                group_0.push(data[j]);
            }
        }

        // calculate the tstat for these groups and add it to the randomised tstats
        calc_tstat(group_0,group_1)
}

// calculate the tstat of the difference of two groups
#[pyfunction]
fn calc_tstat (group_0: Vec<f64>, group_1: Vec<f64>) -> f64 {

    // calculate the amount of data in each group
    let n_0 = group_0.len() as f64;
    let n_1 = group_1.len() as f64;

    // use this to calculate the mean in each group
    let mean_0 = calc_mean(&group_0, n_0);
    let mean_1 = calc_mean(&group_1, n_1);

    // use this to calculate the standard deviation^2 of both groups
    let sigma_0_sqrd = calc_sigma_squared(group_0, mean_0, n_0);
    let sigma_1_sqrd = calc_sigma_squared(group_1, mean_1, n_1);

    // use these to calculate the standard deviation of the difference in means
    let s = (((n_0 - 1.0) * sigma_0_sqrd + (n_1 - 1.0) * sigma_1_sqrd) * (1.0 / n_0 + 1.0 / n_1) / (n_0 + n_1 - 2.0)).sqrt();

    // calculate t-test
    (mean_0 - mean_1) / s
        
}

fn calc_p_value(initial:f64, permutations: Vec<f64>) -> f64 {
    // use the amount and tstats of the permutations and initial tstat to calculate the p value
    let perms = permutations.len() as f64;
    let mut p_value_low : f64 = 0.0;
    let mut p_value_high: f64 = 0.0;
    for i in permutations{
        if i <= initial {
            p_value_high = p_value_high + 1.0 / perms ;
        }
        if i >= initial{
            p_value_low = p_value_low + 1.0/perms;
        }
    }
    if p_value_low < p_value_high {
        p_value_low
    }
    else{
        p_value_high
    }
}



fn calc_mean(group:&Vec<f64>, n: f64) -> f64 {
    // calculate the mean as the sum of the data divided by its length
    let mut mean : f64 = 0.0;
    for i in group {
        mean = mean + i/n;
    }
    mean
}
fn calc_sigma_squared(group: Vec<f64>,mean:f64, n :f64) -> f64{
    // calculate the sigma^2 as the sum of (x-mean)^2 / (N-1)
    let mut sigma_squared : f64 = 0.0;
    for i in group {
        sigma_squared = sigma_squared + (i - mean) * (i - mean) / (n - 1.0);
    }
    sigma_squared
}



/// A Python module implemented in Rust.
#[pymodule]
fn perm_test(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(test, m)?)?;
    m.add_function(wrap_pyfunction!(calc_tstat, m)?)?;
    m.add_function(wrap_pyfunction!(multitest, m)?)?;
    Ok(())
}
