use rand::Rng;
use std::time::{Duration, Instant};

#[derive(Debug)]
pub struct RunResult {
    upper_hits: i32,
    lower_hits: i32,
    total_runs: i32,
    percentage: f64

}

pub fn asymmetric_brownian (
    starting_point: f32, 
    upper_absorption_point: f32,
    lower_absorption_point: f32 ,
    upper_increment: f32 ,
    lower_increment: f32 ,
    p: f64 ,
    time_limit: u64
) -> RunResult {

    let start: Instant = Instant::now();
    let mut up: i32 = 0;
    let mut down: i32 = 0;
    let mut rng: rand::rngs::ThreadRng = rand::thread_rng();

    while start.elapsed() < Duration::from_secs(time_limit) {
        for _ in 0..10000 {
        let mut current_point: f32 = starting_point;
        while current_point < upper_absorption_point && current_point > lower_absorption_point {
            if rng.gen_bool(p) {
                current_point += upper_increment;
            }
            else {
                current_point -= lower_increment;
            }
        }
        if current_point >= upper_absorption_point{
            up += 1;
        }
        else {
            down += 1;
        }
        }
    }
    RunResult {
        upper_hits: up,
        lower_hits: down,
        total_runs: up + down,
        percentage: (up as f64 )/((up + down) as f64)
    }


}

pub fn asymmetric_random_walk_run_limit (
    starting_point: f64, 
    upper_absorption_point: f64,
    lower_absorption_point: f64 ,
    upper_increment: f64 ,
    lower_increment: f64 ,
    p: f64 ,
    run_limit: i32
) -> RunResult {
    
    let mut up: i32 = 0;
    let mut down: i32 = 0;
    let mut rng: rand::rngs::ThreadRng = rand::thread_rng();

    while up + down < run_limit {
        let mut current_point: f64 = starting_point;
        while current_point < upper_absorption_point && current_point > lower_absorption_point {
            if rng.gen_bool(p) {
                current_point += upper_increment;
            }
            else {
                current_point -= lower_increment;
            }
        }
        if current_point >= upper_absorption_point{
            up += 1;
        }
        else {
            down += 1;
        }
        }

    RunResult {
        upper_hits: up,
        lower_hits: down,
        total_runs: up + down,
        percentage: (up as f64 )/((up + down) as f64)
    }
    }
