import midi
from MidiTools import create_chord_progression
from MidiTools import get_notes_per_step
from MidiTools import create_track_from_notes
from MidiTools import create_track_from_melody_notes
from Listener import Environment
from Listener import  Environment
# from sample import predictModel
import csv
import random 
import sys
import numpy as np
import json
import os

min=sys.maxsize
max=-sys.maxsize
DATA_DIR='./data'

MAX_PATTERN_LENGTH = 128
ACTIONS = range(8)
RES = midi.Pattern().resolution#midi分辨率
INIT_NOTE = 0

# 如果SURVEY为真，将为每个和弦进程生成三个旋律:
# 1常规MeRLA旋律 
# 2.MeRLA旋律没有紧张的奖励
# 3. 随机策略的旋律
SURVEY = True

# 返回给定状态下的最佳(对于Q是贪婪的)动作#
# note如果有多个“最佳”行动，将返回随机选择的最佳行动
# 返回格式: tuple with (action, value)
def get_best_action(Q,state):#找到9个行为最大的Q值
    step = state['step']
    prev_note = state['prev_note']
    best_actions = [("", -sys.maxsize)]
    for action in ACTIONS:
        val = Q[step][prev_note][action]
        if val > best_actions[0][1]:
            best_actions = [(action, val)]
        elif val == best_actions[0][1]: 
            best_actions.append((action,val))

    # 返回最佳行动的随机选择
    return random.choice(best_actions)


# 主要功能-运行实验和写入结果到CSV
def run_experiment(env, sims, csv_name, num_episodes, gamma):
    # open csv file
    csvfile = open(csv_name,'w',encoding='utf-8',newline='')
    csvwriter = csv.writer(csvfile)
    # csvwriter = csvwriter.encode()
    # for i in range(sims+1):
    #     i=str(i)
    #     i=i.encode()
    # csvwriter.writerow(i)
    csvwriter.writerow(['' for i in range(sims+1)])
    results = [[0 for i in range(sims)] for j in range(num_episodes)]

    exp_rate = 0.25
    alpha = 0.1

    for sim in range(sims):
        # 随机初始化动作值函数
        Q = [[[] for i in range(8)] for j in range(MAX_PATTERN_LENGTH)]
        for i in range (MAX_PATTERN_LENGTH): # time step
            for j in range(8): # previous action
                Q[i][j] = [0 for l in range(8)]

        # 在歌曲末尾添加注释值(全部相等)
        Q.append([[0 for i in range(8)] for j in range(8)])


        for episode in range(num_episodes):
            # 重置坏境变量
            env.reset()

            # 初始化总奖励和状态
            total_reward = 0.0

            # 从环境中得到初始状态
            state = env.get_init_state(INIT_NOTE)

            # 遍历和弦进行的时间步骤(不包括第一个)
            for step in range(1, len(env.chords)):
                exp_rate = 5.0/(episode+1)
                alpha = 5.0/(episode+1)

                # 使用e-greedy策略选择action
                r = random.random()
                if r < exp_rate:
                    #选择随机行为
                    a = random.choice(ACTIONS)
                else:
                    # 选择最好行为
                    a = get_best_action(Q,state)[0]

                prev_note = state['prev_note']

                # 根据状态、动作和步骤num从环境中获取下一个状态
                next_state = env.get_next_state(state, a)


                #从环境中获得奖励 (由S0,A0得R1)
                reward = env.get_reward(state, a,chord_steps)
                print("奖励：",reward)

                # 将奖励添加到episode的总奖励中
                total_reward += reward

                # 找到下一个状态的最佳行动(w.r.t。Q)
                best_action_next_state = get_best_action(Q,next_state)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

                #将当前的q值存储在TMP变量中 Q估计
                cur_q_val = Q[step][prev_note][a]

                # 更新Q值
                Q[step][prev_note][a] = cur_q_val + (alpha * (reward + (gamma*best_action_next_state[1]) - cur_q_val))

                # 更新状态
                state = next_state

            results[episode][sim] = total_reward

    for episode in results:
        data = episode

        
        data.append(sum(episode)/sims)

        # 将数据行写入CSV文件
        csvwriter.writerow(data)

    csvfile.close()

    return Q


def make_chord(env1, Q_table = None):
    # 重新设置环境变量
    env1.reset()

    # 在MIDI音轨中放置第一个MIDI音符
    # results = [env.note_map[INIT_NOTE] + env.key + 24]
    results = [env1.note_map[INIT_NOTE] + env1.key ]

    # 从环境中得到初始状态
    state = env1.get_init_state(INIT_NOTE)
    h_value=[]
    #遍历和弦进行的时间步骤(不包括第一个和最后一个)
    for step in range(1, len(env1.melody)):
        # choose action with greedy policy if Q_table provided
        # otherwise, take random action
        if Q_table == None:
            a = random.choice(ACTIONS)
        else:
            a = get_best_action(Q_table, state)[0]#找到最大Q对应的行为

        #从环境中获取下一个状态based on state, action, and step num
        next_state = env1.get_next_state(state, a)

        # update state
        state = next_state

        # add MIDI note to melody track
        if a == 8:  # rest
            results.append(-1)
        else:
            # results.append(env.note_map[a] + env.key + 24)
            results.append(env1.note_map[a] + env1.key )
        h_value.append(a)
    print("和弦行为",h_value)
    return results

def make_melody(env, Q_table = None):
    # 重新设置环境变量
    env.reset()

    # 在MIDI音轨中放置第一个MIDI音符
    results = [env.note_map[INIT_NOTE] + env.key + 24]
 

    # 从环境中得到初始状态
    state = env.get_init_state(INIT_NOTE)
    a_value = []
    #遍历和弦进行的时间步骤(不包括第一个和最后一个)
    
    # (暂时代码使用，这里强制和弦长度为8）原本长度len(env.chords)
    for step in range(1, len(env.chords)):
        # 如果Q_table提供了贪心策略，则采取随机操作
       
        if Q_table == None:
            a = random.choice(ACTIONS)
        else:
            a = get_best_action(Q_table, state)[0]#找到最大Q对应的行为

        #从环境中获取下一个状态在当前 state, action, and step num
        next_state = env.get_next_state(state, a)

        # 更新状态
        state = next_state

        # 添加MIDI音符到旋律轨道
        if a == 7:  # rest
            results.append(-1)
        else:
            results.append(env.note_map[a] + env.key + 24)
        a_value.append(a)
    print("旋律行为",a_value)
    return results


####
# 主函数
###

# 通过MeRLA运行的和弦进行的列表
chord_progressions = []


# chords = [(midi.A_4,'minor', 4, 2),
#           (midi.G_4,'major', 4, 2),
#           (midi.F_4, 'major', 4, 3),
#           (midi.G_4, 'major', 4, 1)]

# chord_progressions.append({'chords': chords,
#                             'loops': 2,
#                             'key': midi.A_4,
#                             'scale': 'MIN'})

#卡农和弦1(C G Am Em F C F G)
chords = [(midi.C_4,'major',1,2),
          (midi.G_4,'major',1,2),
          (midi.A_4,'minor',1,2),
          (midi.E_4,'minor',1,2),
          (midi.F_4,'major',1,2),
          (midi.C_4,'major',1,2),
          (midi.F_4,'major',1,2),
          (midi.G_4,'major',1,2)
          
          ]

chord_progressions.append({'chords':chords,
                            'loops':1,
                            'key':midi.C_4,
                            'scale':'MAJ'})

# #稻香的和弦((root,type,length,repeats)
# chords = [(midi.C_4,'major',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.A_4,'minor',1,1),
#           (midi.E_4,'minor',1,1),
#           (midi.F_4,'major',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.A_4,'minor',1,1),
#           (midi.E_4,'minor',1,1),
#           (midi.F_4,'major',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.C_4,'major',1,1)]

# chord_progressions.append({'chords':chords,
#                             'loops':4,
#                             'key':midi.C_4,
#                             'scale':'MAJ'})


# #（16251）（13451）（136251）
# chords = [(midi.C_4,'major',1,1),
#           (midi.A_4,'major',1,1),
#           (midi.D_4,'minor',1,1),
#           (midi.G_4,'minor',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.E_4,'major',1,1),
#           (midi.F_4,'major',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.C_4,'major',1,1),
#           (midi.E_4,'major',1,1),
#           (midi.A_4,'minor',1,1),
#           (midi.D_4,'minor',1,1),
#           (midi.G_4,'major',1,1),
#           (midi.C_4,'major',1,1)]

# chord_progressions.append({'chords':chords,
#                             'loops':4,
#                             'key':midi.C_4,
#                             'scale':'MAJ'})



for i in range(len(chord_progressions)):
    # 初始化一个MIDI模式(包含一个音轨列表)
    pattern = midi.Pattern()

    chords = chord_progressions[i]['chords']
    key = chord_progressions[i]['key']
    scale = chord_progressions[i]['scale']
    loops = chord_progressions[i]['loops']

    
    chords_track = create_chord_progression(chords, loops, RES)#给和弦加三音，7音

   
    
    # pattern.append(chords_track)

    chord_steps = get_notes_per_step(chords_track, RES)#一个由每个时间段的和弦构成的列表

    # 根据chords, key, and scale 创建环境
    env = Environment(chord_steps, key, scale)

    # 通过q-learning获得行动价值Q表
    action_value = run_experiment(env, 1, 'results_chord_prog%d.csv'%i, 1000, 0.9)
    
    # #(暂时代码使用)
    # Q_rule=[]
    # for i in range(1,9):
    #     Q_rule.append(action_value[i])
    # Q_rule_arr=np.array(Q_rule)
    
    # for i in Q_rule_arr:
    #     for j in i:
    #         for k in j:
    #             if k < min:
    #                 min = k
    
    #             if k > max:
    #                 max = k                
                
    # print(min)
    # print(max)
    
    # w3=[]
    # for i in Q_rule_arr:
    #     w2=[]
    #     for j in i:
    #         w1=[]
    #         for k in j:
    #             k=(k-min)/(max-min)
    #             w1.append(k)
    #         w2.append(w1)
    #     w3.append(w2)
    # Q1_arr1=np.array(w3)
    # with open(os.path.join(DATA_DIR, 'q2.json')) as f:
    #     q2_arr1 = json.load(f)
    # q2_arr1_numpy=np.array(q2_arr1)
    # total_Q=Q1_arr1+q2_arr1_numpy
    # fianl_Q=total_Q.tolist()
    #根据Q表学习创建旋律轨道
    melody = make_melody(env,action_value)
    melody_steps = create_track_from_melody_notes(melody, RES)
    pattern.append(melody_steps)
    pattern.append(chords_track)
    # 添加轨道结束事件，并将其附加到所有轨道
    eot = midi.EndOfTrackEvent(tick=1)
    chords_track.append(eot)
    # chord_notes.append(eot)
    melody_steps.append(eot)
    # midi.write_midifile("chord_melody%d_2.mid"%i, pattern)
    # pattern.pop(melody)
    # 强化和弦进行
    # 主要功能-运行实验和写入结果到CSV
    def run_experiment1(env1, sims, csv_name, num_episodes, gamma):
        # open csv file
        csvfile = open(csv_name,'w',encoding='utf-8',newline='')
        csvwriter = csv.writer(csvfile)
        # csvwriter = csvwriter.encode()
        # for i in range(sims+1):
        #     i=str(i)
        #     i=i.encode()
        # csvwriter.writerow(i)
        csvwriter.writerow(['' for i in range(sims+1)])
        results = [[0 for i in range(sims)] for j in range(num_episodes)]
    
        exp_rate = 0.25
        alpha = 0.1
    
        for sim in range(sims):
            # 随机初始化动作值函数
            Q1 = [[[] for i in range(8)] for j in range(MAX_PATTERN_LENGTH)]
            for i in range (MAX_PATTERN_LENGTH): # time step
                for j in range(8): # previous action
                    Q1[i][j] = [random.random() for l in range(8)]
    
            # 在歌曲末尾添加注释值(全部相等)
            Q1.append([[0 for i in range(8)] for j in range(8)])
    
    
            for episode in range(num_episodes):
                # 重置坏境变量
                env.reset()
    
                # 初始化总奖励和状态
                total_reward = 0.0
    
                # 从环境中得到初始状态
                state = env1.get_init_state(INIT_NOTE)
    
                # 遍历和弦进行的时间步骤(不包括第一个)
                for step in range(1, len(env1.melody)):
                    exp_rate = 5.0/(episode+1)
                    alpha = 5.0/(episode+1)
    
                    # choose action with e-greedy policy
                    r = random.random()
                    if r < exp_rate:
                        # choose random action
                        a = random.choice(ACTIONS)
                    else:
                        # choose best action
                        a = get_best_action(Q1,state)[0]
    
                    prev_note = state['prev_note']
    
                    # 根据状态、动作和步骤num从环境中获取下一个状态
                    next_state = env1.get_next_state(state, a)
    
                    #从环境中获得奖励 (由S0,A0得R1)
                    reward = env1.get_reward1(state, a,melody)
                    
                    # print("奖励：",reward)
                    
                    # 将奖励添加到episode的总奖励中
                    total_reward += reward
    
                    # 找到下一个状态的最佳行动(w.r.t。Q)
                    best_action_next_state = get_best_action(Q1,next_state)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    
                    #将当前的q值存储在TMP变量中 Q估计
                    cur_q_val = Q1[step][prev_note][a]
    
                    # 更新Q值
                    Q1[step][prev_note][a] = cur_q_val + (alpha * (reward + (gamma*best_action_next_state[1]) - cur_q_val))
    
                    # 更新状态
                    state = next_state
    
                results[episode][sim] = total_reward
    
        for episode in results:
            data = episode
    
           
            data.append(sum(episode)/sims)
    
            # 写数据
            csvwriter.writerow(data)
    
        csvfile.close()
    
        return Q1
    # 配和弦
    # env1 = Environment1(melody, key, scale)
    #  # 通过q-learning获得行动价值Q表
    # action_value1 = run_experiment1(env1, 1, 'results_chord_prog%d.csv'%i, 1000, 0.9)
    #     # 根据 action-value1 tables学习创建和弦轨道
    # chord_note = make_chord(env1, action_value1)

    # chord_notes= create_track_from_notes(chord_note, RES)

    # # 附加旋律和随机旋律轨道到模式
    # pattern.append(chord_notes)
    # chord_notes.append(eot)
    
    
    
   
    # if SURVEY:
    # #     # 创造独立的环境，没有张力强化，产生旋律
    # #     env_no_tension = Environment(chord_steps, key, scale)
    # #     env_no_tension.set_weights(2, 0.5, 0, 1, 0.5)#为啥传不进参数？
    # #     action_value_no_tension = run_experiment(env_no_tension, 1, 'results_chord_prog%d_no_tension_2.csv' % i, 1000, 0.9)
    # #     melody_steps_no_tension = make_melody(env_no_tension, action_value_no_tension)
    # #     # melody_no_tension = create_track_from_notes(melody_steps_no_tension, RES)

    #     # create random melody track for comparison
    #     random_melody = create_track_from_melody_notes(make_melody(env), RES)

    #     # pattern.append(melody_no_tension)
    #     pattern.append(random_melody)

    #     # melody_no_tension.append(eot)
    #     random_melody.append(eot)
    midi.write_midifile("chord_melody%d_2.mid"%1, pattern)    

    # # Save the pattern to disk
    # midi.write_midifile("chord_no_tension%d_2.mid"%i, pattern)
