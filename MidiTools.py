import midi
import copy

# 创建并返回带有给定和弦进程的MIDI音轨
def create_chord_progression(progression, loops, res):
    # instantiate midi track实例化
    track = midi.Track()

    # 和弦进行的每个循环
    for loop in range(loops):
        # 为进行中的每个和弦
        for (root,type,length,repeats) in progression:
            # 得到第三和第五音符
            third = 0
            fifth = root + 7
            if type == 'major':
                third = root + 4
            elif type == 'minor':
                third = root + 3

            # 对于每个和弦重复
            for i in range(repeats):
                # 创建MIDI注释并附加到轨道
                on = midi.NoteOnEvent(tick=0, velocity=80, pitch=root)
                on3 = midi.NoteOnEvent(tick=0, velocity=80, pitch=third)
                on5 = midi.NoteOnEvent(tick=0, velocity=80, pitch=fifth)
                # on8 = midi.NoteOnEvent(tick=0, velocity=80, pitch=root+12)
                track.append(on)
                track.append(on3)
                track.append(on5)
                # track.append(on8)
                # 实例化MIDI关闭事件并追加到轨道
                off = midi.NoteOffEvent(tick=length*res, pitch=root)
                off3 = midi.NoteOffEvent(tick=0, pitch=third)
                off5 = midi.NoteOffEvent(tick=0, pitch=fifth)
                # off8 = midi.NoteOffEvent(tick=0, pitch=root+12)
                track.append(off)
                track.append(off3)
                track.append(off5)
                # track.append(off8)

    return track


# 接受一个MIDI跟踪对象并返回一个“步骤”列表，其中每个步骤都是一个MIDI事件列表
def split_track(t,res):
    steps = []
    cur_step = []
    for event in t:
        if event.tick == 0:
            cur_step.append(event)
        else:
            steps.append(cur_step)
            for i in range((event.tick//res)-1):
                steps.append([])
            cur_step = [event]

    return steps


#接收一个MIDI跟踪对象并返回一个步骤列表，其中每个步骤都是该步骤中出现的音符列表
def get_notes_per_step(t,res):
    #将轨道events分成几个步骤
    track_s = split_track(t,res)
    steps = []
    notes = []
    for step in track_s:
        for event in step:
            note = event.data[0]
            # 检查事件是否为“note off”事件
            is_off_event = (event.data[1] == 0)
            # 检查是否已经在播放音符
            note_exists = (note in notes)
            # 删除音符如果关闭事件和音符已经被播放
            if is_off_event and note_exists:
                notes.remove(note)
            #添加音符，如果没有关闭事件和音符还没有被演奏
            elif (not is_off_event) and (not note_exists):
                notes.append(note)

        #对结果添加音符列表
        steps.append(copy.deepcopy(notes))

    # 清除轨道末端的空步骤
    for i in reversed(range(len(steps) - 1)):
        if len(steps[i]) == 0:
            steps.pop(i)

    return steps


# 从每个步骤的音符列表中创建一个MIDI音轨
def create_track_from_notes(notes, res):
    track = midi.Track()
    prev_note = notes[0]

    # 加第一个音符
    on = midi.NoteOnEvent(tick=0, velocity=80, pitch=notes[0])
    #加代码
    on1 = midi.NoteOnEvent(tick=0, velocity=80, pitch=notes[0]+4)
    on2 = midi.NoteOnEvent(tick=0, velocity=80, pitch=notes[0]+7)
    #止代码
    track.append(on)
    track.append(on1)#加
    track.append(on2)#加
    delay = 0
    for note in notes[1:]:
        off = midi.NoteOffEvent(tick=res, pitch=prev_note)
        #加
        off1= midi.NoteOffEvent(tick=0, pitch=prev_note+4)
        off2= midi.NoteOffEvent(tick=0, pitch=prev_note+7)
        #止
        # rest
        if note == -1:
            delay += 1
            #加
            # on = midi.NoteOnEvent(tick=0, velocity=80, pitch=0)
            # off = midi.NoteOffEvent(tick=res, pitch=0)
            # track.append(on)
            # track.append(off)
            #止
        else:
            on3 = midi.NoteOnEvent(tick=res * delay, velocity=80, pitch=note)
            #加
            on4 = midi.NoteOnEvent(tick=res*0, velocity=80, pitch=note+4)
            on5 = midi.NoteOnEvent(tick=res * 0, velocity=80, pitch=note+7)
            #止
            track.append(off)
            track.append(off1)#加
            track.append(off2)#加
            track.append(on3)
            track.append(on4)#加
            track.append(on5)#加
            prev_note = note
            delay = 0

    return track
    # track = midi.Track()
    # prev_note = notes[0]

def create_track_from_melody_notes(notes, res):
    track = midi.Track()
    prev_note = notes[0]

    # append first note
    on = midi.NoteOnEvent(tick=0, velocity=80, pitch=notes[0])
    track.append(on)
    delay = 0
    for note in notes[1:]:
        off = midi.NoteOffEvent(tick=res, pitch=prev_note)
        # rest
        if note == -1:
            delay += 1
        else:
            on = midi.NoteOnEvent(tick=res * delay, velocity=80, pitch=note)
            track.append(off)
            track.append(on)
            prev_note = note
            delay = 0

    return track