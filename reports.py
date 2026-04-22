import matplotlib.pyplot as plt


def plot_times(results):
    methods = list(results.keys())
    times = list(results.values())

    plt.figure()
    plt.bar(methods, times)
    plt.xlabel("Method")
    plt.ylabel("Time (seconds)")
    plt.title("Password Cracking Time Comparison")
    plt.show()