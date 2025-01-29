def convert_seconds(seconds):
    hours = seconds // 3600  # 1시간 = 3600초
    minutes = (seconds % 3600) // 60  # 남은 초에서 60으로 나눈 몫이 분
    remaining_seconds = seconds % 60  # 나머지가 초

    return int(hours), int(minutes), int(remaining_seconds)