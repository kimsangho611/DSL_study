# 대신증권API를 활용한 예제들을 확인하고 직접 코딩해본 것

[대신 증권 API관련 클래스 정리 홈페이지] : </br>
1. http://cybosplus.github.io/ </br>
2. http://money2.daishin.com/e5/mboard/ptype_basic/HTS_Plus_Helper/DW_Basic_List_Page.aspx?boardseq=284&m=9508&p=8839&v=8642

[참고자료] :
1. https://wikidocs.net/book/110

## 현재 아나콘다 가상환경의 윈도우 비트수 확인하는 방법
<pre>
<code>
import platform
print(platform.architecture())
</code>
</pre>
실행결과 : ![image](https://user-images.githubusercontent.com/53908335/122172459-b8d36500-cebb-11eb-8413-a19064a8751a.png)

## 아나콘다 가상환경 32-bit으로 설정하는 방법
- 증권 api는 윈도우 32bit 운영체제에서만 동작을 하기 때문에 아나콘다를 32-bit로 설정하여 파이참으로 코딩을 진행한다. 
- `set CONDA_FORCE_32BIT=1`을 아나콘다 프롬프트에 입력 (주의!!!! 32BIT=1은 공백없이 입력)
- `conda create -n "가상환경 이름" python="원하는 버전" anaconda`으로 새로운 가상환경을 설치한다.
- `conda activate "가상환경 이름"`으로 가상환경을 활성화한다.
- 주의!!!!!! : Pycharm은 관리자 모드로 실행해야함

## 주피터 노트북에 가상환경 설치하는 방법
- `python -m ipykernel install --user --name 가상머신이름 --display-name "표시할이름"`
