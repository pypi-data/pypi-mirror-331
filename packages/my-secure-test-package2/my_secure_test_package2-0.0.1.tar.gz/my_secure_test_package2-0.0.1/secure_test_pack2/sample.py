import os


def run_command(user_input):
    # 사용자 입력을 검증 없이 os.system에 전달 - 명령어 주입 취약점
    command = f"echo {user_input}"
    os.system(command)


if __name__ == "__main__":
    user_input = input("Enter a message to echo: ")
    run_command(user_input)
