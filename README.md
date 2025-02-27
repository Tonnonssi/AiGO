## About Code 
This project presents a **dual-agent Gomoku game**, where a 4-DOF robotic arm (end-effector: suction) interacts with a human player in the real world. The robotic arm is controlled by an AI model trained to play Gomoku, enabling it to strategically place stones on the board. Meanwhile, the human opponent directly engages with the system, creating a dynamic and interactive gameplay experience.  

### File structure
```
📂
- Omok       # AlphaZero-based Gomoku AI
- cv         # Computer vision module for real-world interaction
- robotics   # Robotic arm control for physical gameplay
- utils      # Utility functions
- models     # Trained models and loading modules
- web        # Online interaction and web interface

test.ipynb      # Testing and evaluation 
train.ipynb     # Model training 
interact.ipynb  # Human-robot interaction 
```
### Requirement 
```py
# for py
flask                     3.1.0                    
numpy                     2.2.1      
matplotlib                3.10.0 
opencv-python             4.11.0.86          
pandas                    2.2.3                    
pyserial                  3.5                   
scikit-learn              1.6.1                    
scipy                     1.15.0                 
seaborn                   0.13.2                   
serial                    0.0.97                   
torch                     2.5.1
``` 
```cpp
// for arduino
<Servo.h>
```
- [web cam](https://prod.danawa.com/info/?pcode=12508793) 
- [robot arm](https://ko.aliexpress.com/item/1005007386559678.html?spm=a2g0o.productlist.main.15.76b4RakaRakaND&algo_pvid=85321348-9fe0-4f8b-addd-296b5d50c8f3&aem_p4p_detail=202409102006354683620301111830002281303&algo_exp_id=85321348-9fe0-4f8b-addd-296b5d50c8f3-7&pdp_npi=4%40dis%21KRW%2127469%2125650%21%21%21141.96%21132.56%21%402141112417260239956742894ea51d%2112000040533573588%21sea%21KR%210%21ABX&curPageLogUid=hGIF7raV9P0Z&utparam-url=scene%3Asearch%7Cquery_from%3A&search_p4p_id=202409102006354683620301111830002281303_8) + [suction cup](https://ko.aliexpress.com/item/1005006405982303.html?spm=a2g0n.productlist.0.0.6aeb41752MNUKd&browser_id=959a8354f7774087be2289212b388d3c&aff_platform=msite&m_page_id=wxufijqadacaxbrb19444ee325622ecc7b6b15765c&gclid=&pdp_npi=4%40dis%21KRW%2130156%2121909%21%21%21148.29%21107.74%21%402101584917363232487093774ee7ed%2112000037092601986%21sea%21KR%210%21ABX&algo_pvid=87b1efba-feba-4606-bc38-a5e95e5a5dd3#nav-specification)  
    - arduino UNO
    - SENSOR SHIELD V5.0 
- Go board + Go Stone 
### Train info 
> **main default setting** : `N_SELFPLAY=2000`, `N_PLAYOUT=400`, `ResNet x 10`  
- takes 20 hours on an NVIDIA GFORCE 4090  

### How to use
1. **train / test**  
- if you want to use new nn,  
    Import in both `test.ipynb` and `train.ipynb` after adding a new neural network structure (.py) to the `network` folder.  

- if you want to change game setting or hyper params,  
    Change `config.txt`. 

2. **web**  
- run `server.py` in the `web` folder.  

    ```
    python server.py
    ```

- if you want to use new nn on web,  
    set the new model in `models.load_model` after adding a new neural network structure (.py) to the `network` folder and a new model file (.pth/.pt) to the `models` folder *(recommended)*.

3. **Colab**
- put cloned file on g-drive.  
- insert this code below. 
    ```py
    from google.colab import drive
    drive.mount('/content/drive')

    sys.path.append('f_path')
    ```


4. **interact in the real world**
- with both CV and Robotics(even without CV),  
  use `interact.ipynb` file.  

## Result 
📗 [Report (KR)]()  

### In the Real World
![img/Omok.gif](./img/Omok.gif)   
⚠️ The robot was not good at placing the piece accurately at the designated coordinates, so a human manually adjusted its position to ensure smooth CV recognition.
### Game aganist best model-latest model (10000 selfplay)
![img/with_policy.gif](./img/with_policy.gif)   

### Comment 

In matches against humans, the model effectively defended against three-in-a-row threats within the first 16 steps. However, its responsiveness declined in the later stages of the game. As a result, it did not achieve a level of performance that could dominate human opponents, but it demonstrated a certain level of game understanding by securing victories against novice players.

## Member
![img](./img/AiGO.jpeg)
<table border="0" style="width: 100%; text-align: center; border: 1px solid white;">
<tr><td style="border: 1px solid white; padding: 10px;">
        <img src="./img/JiminLee.jpg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">이지민 (Jimin Lee)</b> <br>
        <span style="color: gray; font-size:13px;">👑 팀장  AI • Robotics • Web</span> <br><br>
        <a href="https://github.com/Tonnonssi">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:tonnonssi@gmail.com">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    <td style="border: 1px solid white; padding: 10px;">
        <img src="./img/DoHeeKim.jpeg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">김도희 (DoHee Kim)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI • CV</span> <br><br>
        <a href="https://github.com/doheek1m">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:ellakelly1222@gmail.com">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    <td style="border: 1px solid white; padding: 10px;">
        <img src="./img/HyunseoKim.jpeg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">김현서 (Hyunseo Kim)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  Robotics</span> <br><br>
        <a href="https://github.com/HyunseoKim812">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:rlagustj812@gmail.com">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    </tr><tr><td style="border: 1px solid white; padding: 10px;">
        <img src="./img/SeungyeonLee.jpeg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">이승연 (Seungyeon Lee)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI • Robotics</span> <br><br>
        <a href="https://github.com/sabina381">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:sabina2378@ewhain.net">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    <td style="border: 1px solid white; padding: 10px;">
        <img src="./img/EunnaLee.jpeg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">이은나 (Eunna Lee)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI • CV</span> <br><br>
        <a href="https://github.com/Eunnaeooi">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:len_318@ewha.ac.kr">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    <td style="border: 1px solid white; padding: 10px;">
        <img src="./img/JungyeonLee.jpeg" style="border-radius: 50%;"/><br><br> 
        <b style="font-size:15px">이정연 (Jungyeon Lee)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI </span> <br><br>
        <a href="https://github.com/LeeJungYeonn">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:leejungyeon@ewha.ac.kr">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    </tr></table>

## Reference
- [https://github.com/Jpub/AlphaZero.git](https://github.com/Jpub/AlphaZero.git)  
- [https://github.com/junxiaosong/AlphaZero_Gomoku.git](https://github.com/junxiaosong/AlphaZero_Gomoku.git)   
- [https://github.com/reinforcement-learning-kr/alpha_omok.git](https://github.com/reinforcement-learning-kr/alpha_omok.git)  
