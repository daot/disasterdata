import subprocess
import argparse
from argparse import ArgumentParser

def main(args):
    # Run monitor with queries, then convert the .db to .json
    # Only taking query(s), context, start/end (optional)
    

    ############ Might need to change this path before running ##############

    py3_path = "python3" # Replace this with the path to your virtual env's python3 or just python3
    
    ########################################################################

    # Construct the command strings
    # Assumes the working directory is in this folder

    db_name = f'posts-{"-".join(args.query).replace(" ", "-")}.db'
    queries = ""
    for q in args.query:
        queries = queries + q + " "

    gen_db = (
        f"{py3_path} monitor.py -q {queries} -x \"{args.context}\" -s {args.since} -u {args.until}" 
        if args.since and args.until 
        else f"{py3_path} monitor.py -q {queries} -x \"{args.context}\""
    )
    gen_json = f"{py3_path} db2json.py -d {db_name}"

    # Run in sequence
    print(f'Monitoring will timeout after {args.timeout} seconds.')
    print('Starting monitor.py...')
    try:
        subprocess.run(gen_db, shell=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        print("\n\nScript monitor.py terminated by timeout. Continuing..\n\n")
    print('Converting .db to .json...')
    subprocess.run(gen_json, shell=True)
    print("Done")

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument("-q","--query",type=str,required=True,action="extend",nargs="+",help="the search query",)
    parser.add_argument("-x","--context",type=str,default="The value of QUERY",help="additional query context to help the LLM",)
    parser.add_argument("-s","--since",type=str,help="start date for scraping range")
    parser.add_argument("-u","--until",type=str,help="end date for scraping range")
    parser.add_argument("-t","--timeout",type=float,help="time in seconds to run the scraping script",default=60)
    args = parser.parse_args()
    main(args)