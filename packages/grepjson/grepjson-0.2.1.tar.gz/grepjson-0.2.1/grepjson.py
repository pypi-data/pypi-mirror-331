import argparse
import sys
import json
import pdb


def main():
    parser = argparse.ArgumentParser(description='Interactively inspect or process JSON/JSONL data.')
    parser.add_argument('-l', '--line', action='store_true', help='Treat input as JSONL (one JSON object per line)')
    parser.add_argument('-x', '--exec', type=str, help='Code snippet to execute instead of entering pdb')
    parser.add_argument('-p', '--print', action='store_true', help='Print results of executed code (use with -x)')
    args = parser.parse_args()

    if args.line:
        if args.exec:
            # Process JSONL and execute code for each line
            for line_num, line in enumerate(sys.stdin, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error line {line_num}: {e}", file=sys.stderr)
                    continue

                exec_env = {'obj': obj, '__builtins__': __builtins__}
                try:
                    if args.print:
                        result = eval(args.exec, exec_env)
                        print(result)
                    else:
                        exec(args.exec, exec_env)
                except Exception as e:
                    print(f"Execution error line {line_num}: {e}", file=sys.stderr)
        else:
            # Load all JSONL objects and enter pdb
            objs = []
            for line_num, line in enumerate(sys.stdin, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"JSON decode error line {line_num}: {e}", file=sys.stderr)
            pdb_handler = pdb.Pdb(stdin=open('/dev/tty', 'r'), stdout=sys.stdout)
            pdb_handler.set_trace()
            "pdb: Access parsed objects list as 'objs', type 'c' to exit."
    else:
        # Process single JSON object
        try:
            obj = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}", file=sys.stderr)
            sys.exit(1)

        if args.exec:
            exec_env = {'obj': obj, '__builtins__': __builtins__}
            try:
                if args.print:
                    result = eval(args.exec, exec_env)
                    print(result)
                else:
                    exec(args.exec, exec_env)
            except Exception as e:
                print(f"Execution error: {e}", file=sys.stderr)
        else:
            pdb_handler = pdb.Pdb(stdin=open('/dev/tty', 'r'), stdout=sys.stdout)
            pdb_handler.set_trace()
            "pdb: Access parsed object as 'obj', type 'c' to exit."

if __name__ == '__main__':
    main()