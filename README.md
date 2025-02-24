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

``` 
```cpp
// for arduino

```
- web cam  
- robot arm + suction cup  
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
- 

## Reference
- [https://github.com/Jpub/AlphaZero.git](https://github.com/Jpub/AlphaZero.git)  
- [https://github.com/junxiaosong/AlphaZero_Gomoku.git](https://github.com/junxiaosong/AlphaZero_Gomoku.git)   
- [https://github.com/reinforcement-learning-kr/alpha_omok.git](https://github.com/reinforcement-learning-kr/alpha_omok.git)  

## Result 
📗 [Report (KR)]()  
(시현 움짤)

## Member
![img](./img/AiGO.jpeg)
<table border="0" style="width: 100%; text-align: center; border: 1px solid white;">
<tr><td style="border: 1px solid white; padding: 10px;">
        <img src="./img/JiminLee.jpg" width="120" style="border-radius: 50%;"/><br><br>
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
        <img src="./img/DoHeeKim.jpeg" width="120" style="border-radius: 50%;"/><br><br>
        <b style="font-size:15px">김도희 (DoHee Kim)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI • CV</span> <br><br>
        <a href="https://github.com/doheek1m">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:ellakelly1222@gmail.com">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    </tr><tr><td style="border: 1px solid white; padding: 10px;">
        <img src="./img/HyunseoKim.jpeg" width="120" style="border-radius: 50%;"/><br><br>
        <b style="font-size:15px">김현서 (Hyunseo Kim)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  Robotics</span> <br><br>
        <a href="https://github.com/HyunseoKim812">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:rlagustj812@gmail.com">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    <td style="border: 1px solid white; padding: 10px;">
        <img src="./img/SeungyeonLee.jpeg" width="120" style="border-radius: 50%;"/><br><br>
        <b style="font-size:15px">이승연 (Seungyeon Lee)</b> <br>
        <span style="color: gray; font-size:13px;">팀원  AI • Robotics</span> <br><br>
        <a href="https://github.com/sabina381">
            <img src="https://img.shields.io/badge/github-181717?style=flat-square&logo=github&logoColor=white"/>
        </a> 
        <a href="mailto:sabina2378@ewhain.net">
            <img src="https://img.shields.io/badge/gmail-EA4335?style=flat-square&logo=gmail&logoColor=white"/>
        </a>
    </td>
    </tr><tr><td style="border: 1px solid white; padding: 10px;">
        <img src="./img/EunnaLee.jpeg" width="120" style="border-radius: 50%;"/><br><br>
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
        <img src="./img/JungyeonLee.jpeg" width="120" style="border-radius: 50%;"/><br><br>
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