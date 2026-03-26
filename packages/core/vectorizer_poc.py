import cv2
import numpy as np
import ezdxf
import math

def orthogonalize_line(x1, y1, x2, y2, threshold_deg=10):
    """선을 0도 또는 90도로 강제 스냅하는 함수"""
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # 각도 정규화 (0, 90, 180, -90 등)
    if abs(angle) < threshold_deg or abs(angle - 180) < threshold_deg or abs(angle + 180) < threshold_deg:
        # 수평선으로 간주 (y값 통일)
        return x1, y1, x2, y1
    elif abs(angle - 90) < threshold_deg or abs(angle + 90) < threshold_deg:
        # 수직선으로 간주 (x값 통일)
        return x1, y1, x1, y2
    else:
        # 임계값을 넘어가면 원래 선 유지
        return x1, y1, x2, y2

def run_poc(image_path, output_dxf):
    print(image_path)
    # 1. 이미지 로드 및 그레이스케일 변환
    img = cv2.imread(image_path)
    if img is None:
        print("이미지를 찾을 수 없습니다!")
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. 선 검출 (LSD 사용 - 캐드 도면에 효과적)
    lsd = cv2.createLineSegmentDetector(0)
    lines, _, _, _ = lsd.detect(gray)

    # 3. DXF 파일 생성
    doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    # 결과 시각화용 이미지
    vis_img = img.copy()

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 직교화 알고리즘 적용
            ox1, oy1, ox2, oy2 = orthogonalize_line(x1, y1, x2, y2)
            
            # DXF에 선 추가 (Y축 반전 주의: 이미지 좌표계와 캐드 좌표계 차이)
            msp.add_line((ox1, -oy1), (ox2, -oy2))
            
            # 시각화 (원본=빨강, 보정=초록)
            cv2.line(vis_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 1)
            cv2.line(vis_img, (int(ox1), int(oy1)), (int(ox2), int(oy2)), (0, 255, 0), 2)

    # 4. 저장
    doc.saveas(output_dxf)
    cv2.imwrite('poc_result_view.jpg', vis_img)
    print(f"검증 완료! DXF 저장됨: {output_dxf}")
    print("라인 개수:", len(lines) if lines is not None else 0)

if __name__ == "__main__":
    # 파일 경로는 본인의 환경에 맞게 수정하세요
    run_poc('packages/core/test_input.jpg', 'output_prototype.dxf')