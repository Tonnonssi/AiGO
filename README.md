# Omok  

## Team & Member
AiGO(아이고)  

## Coding Conventions
1. **Class**
   1. Name of Class : PascalCasing  
   2. method : camelCasing + 동사가 먼저 나오는 형식 + 만약 너무 길면 아래다가 주석으로 설명
      ```python
        class Myclass:
            def __init__(self):
                pass
            
            def plus1(self,a):
                '''
                act(a : type ) -> return a + 1 : int
        
                -------
                이 함수는 a에 1을 더하는 함수입니다.
                '''
                return a+1
            ```
       => 주석다는 방법 :
       함수명 ( input 파라미터 나열, :로 타입 명시) -> return output 파라미터 : 타입 명시
       
       ----------로 내용 분리  
       함수 작동 원리 및 사용하는 곳 설명, 예제가 있어도 됨   
   3. attribute : snake_casing
   4. hidden method / attribute : `_` 를 앞에다 붙여 클래스 내부에서 사용함을 명시함 
   5. 인스턴스 : 언더바, 명확한 이름 지향 
  
2. **Attribute** : snake_casing     
3. **method** : camelCasing   
3. **하이퍼파라미터** : UPPER_CASE   
4. **들여쓰기** : 4칸   
5. **문자열** : 외부로 출력되는 애는 “ ”, 나머지는 ‘ ’  
