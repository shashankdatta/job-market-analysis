import indeed
import sys
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python run.py <start_page_num> <end_page_num>")
        sys.exit(1)
    start_page_num = int(sys.argv[1])
    end_page_num = int(sys.argv[2])
    for page_num in range(start_page_num, end_page_num+1):
        indeed.save_jobs(page_num)

if __name__ == "__main__":
    main()