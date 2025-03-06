import ffmpegx


def main():
    ffmpegx.seek("00:00:10", "00:01:10").input("input.mp4").output(
        "output.mp4"
    ).display()


if __name__ == "__main__":
    main()
