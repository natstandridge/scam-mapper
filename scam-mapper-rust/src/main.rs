use clap::Parser;

/// Simple program to greet a person
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
   /// Name of the person to greet
   #[arg(short, long)]
   url: String,
}

struct DigitBlockParser {
    in_block: bool,
    current_block: String,
    blocks: Vec<String>,
}

impl DigitBlockParser {

    fn new() -> DigitBlockParser {
        DigitBlockParser { in_block: false, current_block: String::new(), blocks: Vec::new() }
    }

    fn replace_int_blocks_with_token(&mut self, input_string: String, min_block_len: usize, token: String) -> String {

        self.in_block = false;

        for chr in input_string.chars() {
            let status_str = match self.in_block {
                true => "in block",
                false => "out of block"
            };

            match chr.is_digit(10) {
                true => {
                    self.current_block.push(chr.clone());
                    self.in_block |= true;
                },
                false => {
                    match self.in_block {
                        true => {
                            self.in_block = false;
                            
                            let cb = self.current_block.clone();
                            if cb.len() > min_block_len {
                                let mut src: Vec<String> = vec![cb];
                                self.blocks.append(&mut src);
                            }
                            self.current_block = String::new();
                        },
                        false => {}
                    }

                }
            }
        }

        self.blocks.sort();

        let mut output_string = input_string.clone();

        for b in self.blocks.iter() {
            output_string = output_string.replace(b, &token);
        }

        println!("blocks: {:#?}", self.blocks);
        println!("output string: {:#?}", output_string);
        

        output_string


    }
}



fn main() {
    let args = Args::parse();

    println!("{:?}", args);

    let mut dbp = DigitBlockParser::new();

    dbp.replace_int_blocks_with_token("123testtest45testhello09987765sdf453".to_string(), 3, "~".to_string());
}
