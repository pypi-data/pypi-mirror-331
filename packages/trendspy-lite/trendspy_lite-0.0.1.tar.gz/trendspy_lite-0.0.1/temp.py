import memory_profiler

@memory_profiler.profile
def main():
    print(1 + 2)
    from trendspy import Trends
    tr = Trends(request_delay=10.)
    data = tr.interest_over_time(["python"])
    print(data)


if __name__ == '__main__':
    main()