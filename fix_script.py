# 파일 수정 스크립트
import re

# 원본 파일 읽기
with open('weather_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# world_col이 포함된 라인들을 제거
lines = content.split('\n')
filtered_lines = []
skip_lines = 0

for i, line in enumerate(lines):
    # world_col이 포함된 라인들과 그 다음 2라인 제거
    if 'world_col' in line:
        skip_lines = 3  # 현재 라인 + 다음 2라인
        continue
    
    if skip_lines > 0:
        skip_lines -= 1
        continue
    
    filtered_lines.append(line)

# 수정된 내용을 파일에 저장
fixed_content = '\n'.join(filtered_lines)

# 빈 if 블록 수정
fixed_content = re.sub(
    r'if location_search:\s*\n\s*with st\.spinner',
    r'if location_search:\n        with st.spinner',
    fixed_content
)

with open('weather_app_fixed.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("파일 수정 완료!")