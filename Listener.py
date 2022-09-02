# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 20:39:05 2022

@author: F413Y
"""

import midi
import operator
import math
import numpy as np
# from sample import predictModel
# 每个音符演奏时所产生的张力
TENSION = [1, 1.2, 1, 1.4, 1, 1.1, 1.6, 1, 1]

INTERVAL_VALS = [0, 1, 0.5, -1, 1, -1, -1, -1]

CHORD_FITS = [1, -1, 1, -2, 1, -1, -2]

class Environment:
    chords = []
    note_map = []

    weights = {
        'chord_fit': 2,
        'restlessness': 0.5,
        'tension': 1,
        'interval': 1,
        'clutter' : 0.5
    }

    key = midi.C_4
    scale = 'MAJ'

    last_played = 0
    tension = 0
    restlessness = 0
    clutter = 0

    def __init__(self, chords, key, scale):
        self.key = key
        self.scale = scale

        if scale == 'MAJ':
            self.note_map = [0, 2, 4, 5, 7, 9, 11, 12]#大调
        elif scale == 'MIN':
            self.note_map = [0, 2, 3, 5, 7, 8, 10, 12]#小调

        self.chords = self.make_key_relative(chords)

    def make_key_relative(self, chords):
        result = []
        for chord in chords:
            notes = []
            for note in chord:
                notes.append(self.note_map.index((note-self.key)%12))
            result.append(notes)

        return result

    def set_weights(self, chord_fit, restlessness, tension, interval, clutter):
        self.weights['chord_fit'] = chord_fit
        self.weights['restlessness'] = restlessness
        self.weights['tension'] = tension
        self.weights['interval'] = interval
        self.weights['clutter'] = clutter


    def reset(self):
        self.tension = 0
        self.restlessness = 0
        self.clutter = 0

    def get_init_state(self, init_note):
        first_state = {'step': 1,
                     'prev_note': init_note}

        return first_state

    def get_next_state(self, state, action):
        # 从状态中提取值
        step = state['step']

        # 构建新的状态
        new_state = {'step': step + 1,
                     'prev_note': action}

        return new_state
    
   


    def get_reward(self, state, action,chord_steps):
        reward = 0
        compare_note=['C','D','E','F','G','A','B','']

        # preseven_chord=[0,0,0,0]
        # extract values from new state
        step = state['step']
        chord = self.chords[step]
        # chords = chord_steps
        # seven_chord =[self.key,self.key]
        # if self.scale == 'MAJ':
        #     self.note_map = [0, 2, 4, 5, 7, 9, 11, 12]
        # elif self.scale == 'MIN':
        #     self.note_map = [0, 2, 3, 5, 7, 8, 10, 12]
        seven_chord = chord_steps[step]
        # seven_chord = []
        # seven_chord.append(self.key)
        # # s= self.note_map[self.chords[step][1]]
        # seven_chord.append(self.key+self.note_map[self.chords[step][1]])
        # seven_chord.append(self.key+self.note_map[self.chords[step][2]])
        # seven_chord.append(self.key+self.note_map[self.chords[step][3]]+12)
        # seven_chord = [self.key,self.key+self.note_map(self.chords(1)),self.key+self.note_map(self.chords(2)),self.key+self.note_map(self.chords(3))+12]
        
        chord_root = chord[0]
        prev_note = state['prev_note']
        note = action

        #如果沉默，增加紧张感
        if note == 8:
            # reset clutter
            self.clutter = 0
            # 增加当前张力的倍数
            self.tension += TENSION[8]*self.tension
            if prev_note == 6:
                reward -= self.weights['interval']
        else:
            #如果前一个音符是休止符，看看再前面一个音符
            if prev_note == 8:
                prev_note = self.last_played
            else:
                # 应用杂乱惩罚并更新杂乱
                reward -= self.weights['clutter']
                self.clutter += 1

            # （音符间隔 前后两个音）旋律的前后两个音
            note_interval = abs(note - prev_note)
            reward += self.weights['interval'] * INTERVAL_VALS[note_interval]
            
            #reward chord harmonious
            
            
            #增加超强级数
            
            if step ==1:
                global  preseven_chord
                preseven_chord=[0,0,0,0]
            elif step!=1 and prev_note!=8:
                if step>2:
                    print(chord_steps[step-2])
                    print(preseven_chord)
                    print(seven_chord)
                repeat=0
                # while( operator.eq(preseven_chord,seven_chord)):
                for i in preseven_chord:
                    # print(preseven_chord)
                    
                    if i not in seven_chord:
                        repeat+=1
                    if repeat==4:
                        reward-=0.5
                        
                    # for j in seven_chord:
                    #     while i!=j:
                    #         reward -= 0.5
                    #     break
                
                
                # print(reward)
            # reward note distance
            # print(preseven_chord[0])
            # print(preseven_chord[1])
            # if preseven_chord[0]!=0:
                
            # # print(a)
            #     reward-=np.log((4**(abs(preseven_chord[0]-seven_chord[0]))+4**(abs(preseven_chord[1]-seven_chord[1]))+4**(abs(preseven_chord[2]-seven_chord[2]))+4**(abs(preseven_chord[3]-seven_chord[3]))))
            # # reward-=math.log(,math.e)
            # #reward paraline octave
            # # print(abs(preseven_chord[0]-seven_chord[0]))
            # if (abs(preseven_chord[0]-seven_chord[0])==0 or abs(preseven_chord[1]-seven_chord[1])==0 or (preseven_chord[2]-seven_chord[2])==0 or (preseven_chord[3]-seven_chord[3])==0) and \
            #     (abs(preseven_chord[0]-seven_chord[0])==7 or abs(preseven_chord[1]-seven_chord[1])==7 or (preseven_chord[2]-seven_chord[2])==7 or (preseven_chord[3]-seven_chord[3])==7):
            #         reward -=3
            # reward progression
            if step ==1:
                global pre_index
                pre_index = [0,0,0,0]
            elif step!=1 and prev_note!=8:
                tonal=[0,1,0,1,2,0,4,1]
                # print("哈哈",tonal(pre_index[0]))
                if tonal[pre_index[0]]-tonal[chord[0]]==-1 or tonal[pre_index[0]]-tonal[chord[0]]==-1:
                    reward+=5;
            # （和弦间隔，垂直两个音）
            chord_interval = (note - chord_root)%7
            reward += self.weights['chord_fit'] * CHORD_FITS[chord_interval]

            # 施加压力奖励(释放)或增加(构建)压力
            if (note == 0 or note == 7) and chord_root == 0:
                if prev_note == 8:
                    reward += TENSION[8] * self.weights['tension'] * self.tension
                else:
                    reward += self.weights['tension'] * self.tension
                self.tension = 0
            elif note == 4 and (chord_root == 0 or chord_root == 4):
                reward += self.tension / 2
                self.tension = self.tension / 2
            else:
                self.tension *= TENSION[note]

            self.last_played = note

        # （前一个和后一个音符相等时受到惩罚）
        if note == prev_note:
            self.restlessness += 1
        else:
            self.restlessness = 0
        reward -= self.restlessness * self.weights['restlessness']
        preseven_chord = seven_chord#数字式音符
        pre_index = chord

        return reward
