
mod brownian;

  
fn main() {

    for _ in 0..5 {
    let result  = brownian::asymmetric_random_walk_run_limit (
        5.0,
        5.5,
        0.0,
        0.5,
        1.0,
        0.5,
        1_000
    );
    println!("{:?}", result );

    }

}
