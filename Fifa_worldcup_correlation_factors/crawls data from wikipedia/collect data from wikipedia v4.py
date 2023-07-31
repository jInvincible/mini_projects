import re
import bs4
import requests
import pandas as pd

# variables
# group_list cdata
cdata_group_list = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5',
                    'Group 6', 'Group 7', 'Group 8', 'Group A', 'Group B',
                    'Group C', 'Group D', 'Group E', 'Group F', 'Group G',
                    'Group H'
                    ]

# knockout_list cdata
cdata_knockout_list = ['Semi-finals', 'Final', 'Preliminary round',
                       'Quarter-finals', 'Semi-finals',
                       'Match for third place',
                       'First round', 'Round of 16', 'Third place',
                       'Play-off for third place', 'Third place play-off']

REPLACEMENTS = [
    ('img', {'alt': 'downward-facing red arrow'}, 'b', {}, 'O'),
    ('img', {'alt': 'upward-facing green arrow'}, 'b', {}, 'I'),
    ('img', {'alt': 'Yellow card'}, 'b', {}, 'Y'),
    ('img', {'alt': 'Yellow-red card'}, 'b', {}, 'RSY'),
    ('img', {'alt': 'Red card'}, 'b', {}, 'R'),
    ('img', {'title': 'Goal'}, 'b', {}, 'G'),
    # ('style', {}, 'b', {}, '')
]

## define corresponding pattern for each column of the sample dataframe to check
# role_pattern = re.compile('\\b[A-Z]{2}\\b|Manager.')
# snumber_pattern = re.compile('\\b[\d]{1,2}\\b')
# name_pattern = re.compile('[\sa-zA-Z\-]{3,}[\sa-zA-Z\-]{3,}(\(c\))?')
# card_pattern = re.compile(
#     '\\b(Y\\xa0[\d]{1,2})|\\bR(\\xa0[\d]{1,2})|\\b(RSY)\\xa0[\d]{1,2}')
# in_out_pattern = re.compile('\\b[O|I](\\xa0)[\d]{1,2}')
pattern_list = ['\\b[A-Z]{2}\\b|.+Manager.+',
                '\\b[\d]{1,2}\\b',
                '[\sa-zA-Z\-]{3,}[\sa-zA-Z\-]{3,}(\(c\))?',
                '\\b(Y\\xa0[\d]{1,2})|\\bR(\\xa0[\d]{1,2})|\\b(RSY)\\xa0[\d]{1,2}',
                '\\b[O|I](\\xa0)[\d]{1,2}'
                ]
pattern = '[\sa-zA-Z\-]{3,}[\sa-zA-Z\-]{3,}(\(c\))?'

df_group_starting = pd.DataFrame(None, columns=['MatchID',
                                                'Refer',
                                                'HT Role',
                                                'HT Captain',
                                                'HT Shirt Number',
                                                'HT Fullname',
                                                'HT Discipline',
                                                'HT In_Out',
                                                'HT Goal',
                                                'AT Goal',
                                                'AT Role',
                                                'AT Captain',
                                                'AT Shirt Number',
                                                'AT Fullname',
                                                'AT Discipline',
                                                'AT In_Out',
                                                'Home Team',
                                                'Away Team',
                                                ])

df_group_matches = pd.DataFrame(None, columns=['Year',
                                               'Stage',
                                               'Date',
                                               'Time',
                                               'Stadium',
                                               'Location',
                                               'Home Team',
                                               'HT Goals',
                                               'AT Goals',
                                               'Away Team',
                                               'Match Attendance',
                                               'MatchID',
                                               'Refer'
                                               ])

y_ff = [
    '1930',
    '1934',
    '1938',
    '1950',
    '1954',
    '1958',
    '1962',
    '1966',
    '1970',
    '1974',
    '1978',
    '1982',
    '1986',
    '1990',
    '1994',
    '1998',
    '2002',
    '2006',
    '2010',
    '2014',
    '2018'
]


# end variables

# custom functions
def replace_tags_with_labels(html, replacements=REPLACEMENTS):
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    for tag, search_attr, new_tag, new_attr, new_string in \
            replacements:
        for node in soup.find_all(tag, search_attr):
            replacement = soup.new_tag(new_tag, **new_attr)
            replacement.string = new_string
            node.replace_with(replacement)
    return str(soup)


def allocate_corresponding_data_columns(data, pattern_list=pattern_list):
    # create a_dic to receive value
    # 0: role pattern = '\\b[A-Z]{2}\\b|.*Manager.*'
    # 1: shirt number pattern = '\\b[\d]{1,2}\\b'
    # 2: fullname pattern = '[\sa-zA-Z\-]{3,}[\sa-zA-Z\-]{3,}(\(c\))?'
    # 3: discipline pattern = '\\b(Y\\xa0[\d]{1,2})|\\bR(\\xa0[\d]{1,2})|\\b(RSY)\\xa0[\d]{1,2}'
    # 4: in_out pattern = '\\b[O|I](\\xa0)[\d]{1,2}'
    
    a_dic = {0: [], 1: [], 2: [], 3: [], 4: []}
    
    #compare input data with each pattern then assign the matching to corresponding position(key) with the corresponding value(key value)
    for i, pattern in enumerate(pattern_list):        
        for text in data:
            for word in text:
                if re.search(pattern, word): # re.search(pattern, word)
                    a_dic[i] += [word]
                    break
                elif word == text[-1]:
                    a_dic[i] += ['None']
                    break           
    return a_dic


def cleanup_fgoals(fgoals_collect):
    for _ in range(4):
        index_to_remove = []
        for i, word in enumerate(fgoals_collect):
            if word == 'Penalty kick (association football)' or word == 'Own goal':
                index_to_remove.append(i)
            elif len(word) <= 3:
                index_to_remove.append(i)
            elif word in fgoals_collect[i - 1] and i != 0:
                index_to_remove.append(i)

        index_to_remove.sort(reverse=True)
        for i in index_to_remove:
            fgoals_collect.pop(i)
    # for testing only {'Romário':["G 26'", "G 52'\xa0(pen.)"]}
    star_event_dict = {}
    key = ''
    for name in fgoals_collect:
        try:
            re.search('\\bG\s\d+', name).group(0)
            name.replace('\xa0','')
            star_event_dict[key] += [name]
        except AttributeError:
            if len(name.split('(')) > 0:
                name = name.split('(')[0]
            star_event_dict[name] = []
            key = name

    star = list(star_event_dict)
    event = []
    for key in star:
        str1 = ', '.join([str(ele) for ele in star_event_dict[key]])
        event.append(str1)

    return star, event


def check_loc(df_name, starnameh, starnamea, fullname_h, fullname_a,
              g_event_h, g_event_a):
    row_value_dict_h = {}
    row_value_dict_a = {}
    for row_event, content_h in enumerate(df_name[g_event_h]):
        content_h = str(content_h)
        if content_h != 'None' and content_h != 'nan':
            if '(o.g.)' not in content_h:
                if df_name[df_name[fullname_h] == df_name.loc[row_event][starnameh]].size > 0:
                    row_index = df_name[df_name[fullname_h] == df_name.loc[row_event][starnameh]].index[0]
                    row_value_dict_h[row_index] = content_h
            else:
                if df_name[df_name[fullname_a] == df_name.loc[row_event][starnameh]].size > 0:
                    row_index = df_name[df_name[fullname_a] == df_name.loc[row_event][starnameh]].index[0]
                    row_value_dict_a[row_index] = content_h
    for row_event, content_a in enumerate(df_name[g_event_a]):
        content_a = str(content_a)
        if content_a != 'None' and content_a != 'nan':
            if '(o.g.)' not in content_a:
                if df_name[df_name[fullname_a] == df_name.loc[row_event][starnamea]].size > 0:
                    row_index = df_name[df_name[fullname_a] == df_name.loc[row_event][starnamea]].index[0]
                    row_value_dict_a[row_index] = content_a
            else:
                if df_name[df_name[fullname_h] == df_name.loc[row_event][starnamea]].size > 0:
                    row_index = df_name[df_name[fullname_h] == df_name.loc[row_event][starnamea]].index[0]
                    row_value_dict_h[row_index] = content_a
    return row_value_dict_h, row_value_dict_a


# end custom functions

# main
url_wiki = 'https://en.wikipedia.org/wiki/'
urls = [f'{url_wiki}{y}_FIFA_World_Cup' for y in y_ff]
for url_main in urls:
    # url_main = 'https://en.wikipedia.org/wiki/2018_FIFA_World_Cup'
    # year base on url link
    match_year = re.search('\d+', url_main).group(0)
    url_temp = url_main

    # request content
    r_main = requests.get(url_main)

    # replace all img tags to corresponding labels
    soup_main = bs4.BeautifulSoup(replace_tags_with_labels(r_main, replacements=
    REPLACEMENTS).replace('\n', '').replace('\r', ''), 'html.parser')
    soup_main = bs4.BeautifulSoup(soup_main.encode('UTF-8'), 'html.parser')

    # create group_list and knockout_list to get list of navigating url
    headline_group = soup_main.find_all(attrs='mw-headline',
                                        text=cdata_group_list)

    # drop duplicate in group list and sort ascending
    group_list = list(set([group.text for group in headline_group]))
    group_list.sort()

    # 1950 World cup Final stage = final round
    if '1950' in url_main:
        all_round_list = group_list + ['final round']
    # elif '1934' in url_main or '1938' in url_main:
    #     all_round_list = group_list + ['final_tournament']
    elif '1934' in url_main or '1938' in url_main:
        group_list = ['qualification']
        all_round_list = group_list + ['final tournament']
    else:
        all_round_list = group_list + ['knockout stage']


    # # for testing-only, remove for full execute
    # all_round_list = ['Group 1']

    for rounds in all_round_list:
        # make a backtup url
        url_temp1 = url_main
        rounds_temp1 = rounds.replace(' ', '_')
        url_main = f'{url_main}_{rounds_temp1}'
        # request each group detail content
        # ex: https://en.wikipedia.org/wiki/2010_FIFA_World_Cup_Group_A
        r_main = requests.get(url_main)

        # soup r_main and reformat/encode(UTF-8) ++
        soup_main = bs4.BeautifulSoup(replace_tags_with_labels(r_main,
               replacements=REPLACEMENTS).replace('\n', ''), 'html.parser')
        soup_main = bs4.BeautifulSoup(soup_main.encode('UTF-8'), 'html.parser')
        # get tags of all matches
        all_matches_info = soup_main.findAll(attrs='footballbox')

        for match_info in all_matches_info:
            match_stage = rounds

            # get match_id, for missing matchid, receive 'missing'
            if match_info.find('a', text='Report') == None:
                if match_info.find(attrs='fscore').text.find('awarded') == -1:
                    match_id = 'missing'
                else:
                    match_id = 'awarded'
                match_refer = 'missing'
            else:
                match_id = re.search(
                    '[\d]+(?=\/$)|[\d]+$|[\d]+(?=\/i)|[\d]+(?=\/r)|[\d]+(?=/\#)',
                    match_info.find('a', text='Report')['href']).group(0)
                match_refer = match_info.find('a', text='Report')['href']
            # name : home team + away team
            home_team_name = match_info.find(attrs='fhome').text.replace('\xa0','')
            away_team_name = match_info.find(attrs='faway').text.replace('\xa0','')

            # check tag_fscore_a and receive HT F Score + AT F Score + time
            tag_fscore_has_link = match_info.find(attrs='fscore').find('a')
            slash_text = re.search('[\D]+', match_info.find(attrs='fscore').text).group(0)

            # when tag_fscore_a persist
            if tag_fscore_has_link != None:
                a_href = tag_fscore_has_link['href']
                # handle 2018, 2014, 2010, 2006, 1970, 1954 note, extra time note, overtime
                if '2018' not in a_href and '2014' not in a_href and '2010' not in a_href and '2006' not in a_href and '1970' not in a_href and '1954' not in a_href and 'Extra_time' not in a_href and 'Overtime' not in a_href and '1934' not in url_main:
                    match_id = f"{tag_fscore_has_link.text} detail in {tag_fscore_has_link['href']}"
                    home_team_f_score = f"{tag_fscore_has_link.text} detail in {tag_fscore_has_link['href']}"
                    away_team_f_score = f"{tag_fscore_has_link.text} detail in {tag_fscore_has_link['href']}"
                    match_time = f"{tag_fscore_has_link.text} detail in {tag_fscore_has_link['href']}"
                else:
                    home_team_f_score = \
                        match_info.find(attrs='fscore').text.split(slash_text)[0]
                    away_team_f_score = \
                        match_info.find(attrs='fscore').text.split(slash_text)[1]
                    if '1934' in url_main or '1938' in url_main:
                        match_time = 'missing'
                        check_time = 'missing'
                    else:
                        match_time = re.search('[\d]{1,2}:[\d]{1,2}', match_info.find(
                            'div', attrs='ftime').text).group(0)
            else:
                home_team_f_score = \
                match_info.find(attrs='fscore').text.split(slash_text)[0]
                away_team_f_score = \
                match_info.find(attrs='fscore').text.split(slash_text)[1].replace('(d)','')
                if '1934' in url_main or '1938' in url_main:
                    match_time = 'missing'
                    check_time = 'missing'
                else:
                    match_time = re.search('[\d]{1,2}:[\d]{1,2}', match_info.find(
                        'div', attrs='ftime').text).group(0)
                    check_time = match_info.find('div', attrs='ftime').text

            # date
            # cut redundant of date
            cut_date = re.search('.+(?=\()', match_info.find(attrs='fdate').text)
            if cut_date != None:
                match_date = cut_date.group(0)
            else:
                match_date = match_info.find(attrs='fdate').text

            # get fhgoal, fagoal tags
            # for empty fgoals
            if len(str(match_info.find(attrs={'class': ['fgoals']}).text)) > 5:
                fgoals = match_info.find(attrs={'class': ['fgoals']})
                fhgoal = fgoals.find(attrs={'class': 'fhgoal'})
                fagoal = fgoals.find(attrs={'class': 'fagoal'})
                fhgoal_collect = [
                    i.attrs['title'].strip() if i.name == 'a' else i.text.strip()
                    for i in fhgoal.select('a[title],span')]
                fagoal_collect = [
                    i.attrs['title'].strip() if i.name == 'a' else i.text.strip()
                    for i in fagoal.select('a[title],span')]

                # cleanup and allocate data hgoal and agoal
                hgoal_event = cleanup_fgoals(fhgoal_collect)
                agoal_event = cleanup_fgoals(fagoal_collect)

                # make df_fhgoal, df_fagoal as table receive starnames and goal
                # events for both team
                df_hgoal = pd.DataFrame(
                    {'Starname_h': hgoal_event[0], 'Goal_eventh': hgoal_event[1]})
                df_agoal = pd.DataFrame(
                    {'Starname_a': agoal_event[0], 'Goal_eventa': agoal_event[1]})
            else:
                empty_hgoal = {'Starname_h': [], 'Goal_eventh': []}
                empty_agoal = {'Starname_a': [], 'Goal_eventa': []}
                df_hgoal = pd.DataFrame(empty_hgoal)
                df_agoal = pd.DataFrame(empty_agoal)

            # stadium
            soup_stadium = match_info.find(attrs='fright')
            match_stadium = \
            soup_stadium.find('div', attrs={'itemprop': 'location'}
                              ).text.split(',')[0]

            # location
            match_location = \
            soup_stadium.find('div', attrs={'itemprop': 'location'}
                              ).text.split(',')[1]

            # attendance
            if match_id == 'w/o detail in /wiki/Walkover':
                match_attendance = f"{tag_fscore_has_link.text} detail in {tag_fscore_has_link['href']}"
            elif match_info.find(attrs='fscore').text.find('awarded') != -1:
                match_attendance = 'missing'
            else:
                match_attendance = re.search('[\d,]+', re.search('Attendance[^<>]+',
                                                             str(soup_stadium.findAll(
                                                                 'div'))).group(
                0)).group(0)

            # get starting tag
            # tag_starting_table = match_info.findNextSiblings('table', limit=2)[1]
            # change tag_starting location in some match by matchid
            if match_id in ['1689', '2350', '2454', '2352', '2431', '2220',
                            '2196', '2252', '1146']:
                tag_starting_table = match_info.nextSibling.nextSibling.nextSibling
            elif match_id == 'w/o detail in /wiki/Walkover':
                pass
            else:
                tag_starting_table = match_info.nextSibling.nextSibling

            # for some matches without starting info
            if tag_starting_table.name not in ['h3', 'h2', 'link', 'style']:
                # get tag of home team starting
                # change tag_h and tag_a in some match by matchid
                # WC 1934, 1938
                if rounds == 'qualification':
                    hdata1 = {1:[], 2:[], 3:[], 4:[], 5:[]}
                    df_hdata = pd.DataFrame(hdata1)
                    df_adata = df_hdata.copy()

                else:
                    if match_id in ['2350', '2352']:
                        tag_h = tag_starting_table.tr.tr.findChildren("td",
                                         recursive=False)[0]
                    else:
                        tag_h = \
                            tag_starting_table.tr.findChildren("td",
                                           recursive=False)[0]

                    # get tag of away team starting
                    if match_id in ['2350', '2352']:
                        tag_a = tag_starting_table.tr.tr.findChildren("td",
                                         recursive=False)[-1]
                    else:
                        tag_a = tag_starting_table.tr.findChildren("td",
                                         recursive=False)[-1]

                    # collect starting data of home team: role, shirt number,
                    # fullname, discipline, in_out
                    # -> df_hdata
                    row = []
                    hdata1 = []
                    for tr in tag_h.find_all('tr'):
                        td = [i.text for i in tr.find_all('td')]
                        row = [i for i in td]
                        hdata1.append(row)
                    hdata = allocate_corresponding_data_columns(hdata1)
                    df_hdata = pd.DataFrame(hdata)
                    if len(df_hdata) > 2:                        
                        h_manager_name = df_hdata.iloc[-1,2]
                        df_hdata.iloc[-2, 0] = 'Manager'
                        df_hdata.iloc[-2, 2] = h_manager_name
                        df_hdata = df_hdata.drop(index=len(df_hdata) - 1)

                    # collect starting data of away team: role, shirt number,
                    # fullname, discipline, in_out
                    # -> df_adata tag_a.table.findAll('tr')
                    row = []
                    adata1 = []
                    for tr in tag_a.table.find_all('tr'):
                        td = [i.text for i in tr.find_all('td')]
                        row = [i for i in td]
                        adata1.append(row)
                    adata = allocate_corresponding_data_columns(adata1)
                    df_adata = pd.DataFrame(adata)
                    if len(df_adata) > 2:
                        a_manager_name = df_adata.iloc[-1,2]
                        df_adata.iloc[-2, 0] = 'Manager'
                        df_adata.iloc[-2, 2] = a_manager_name
                        df_adata = df_adata.drop(index=len(df_adata) - 1)

                # make dataframe by concat match_id, null series df_hdata,
                # null series, null series, null series, df_ahata
                # -> df_starting
                df_starting = pd.concat(
                    [pd.Series(match_id), pd.Series(match_refer),pd.Series(None, name='HT Captain', dtype='int64'),
                     df_hdata, pd.Series(None, name='HT Goal', dtype='float64'),
                     pd.Series(None, name='AT Goal', dtype='float64'),
                     pd.Series(None, name='AT Captain', dtype='int64'), df_adata, pd.Series(None, name='Home Team', dtype='float64'), pd.Series(None, name='Away Team', dtype='float64')], axis=1)
                df_starting.columns = ['MatchID',
                                       'Refer',
                                       'HT Captain',
                                       'HT Role',
                                       'HT Shirt Number',
                                       'HT Fullname',
                                       'HT Discipline',
                                       'HT In_Out',
                                       'HT Goal',
                                       'AT Goal',
                                       'AT Captain',
                                       'AT Role',
                                       'AT Shirt Number',
                                       'AT Fullname',
                                       'AT Discipline',
                                       'AT In_Out',
                                       'Home Team',
                                       'Away Team',
                                       ]

                # paste match_id for all value in column MatchID
                df_starting['MatchID'] = match_id
                df_starting['Refer'] = match_refer
                df_starting['Home Team'] = home_team_name
                df_starting['Away Team'] = away_team_name
                
                # cut symbol (c) from fullname to captain
                copy_of_ht_fullname = df_starting['HT Fullname'].copy()
                copy_of_ht_captain = df_starting['HT Captain'].copy()
                for i, name in enumerate(copy_of_ht_fullname):
                    cap_symbol = '(c)'
                    name = str(name)
                    if cap_symbol in name:
                        copy_of_ht_captain[i] = 1
                        new_name_h = name.split(cap_symbol)[0]
                        copy_of_ht_fullname[i] = new_name_h
                df_starting['HT Fullname'] = copy_of_ht_fullname
                df_starting['HT Captain'] = copy_of_ht_captain

                copy_of_at_fullname = df_starting['AT Fullname'].copy()
                copy_of_at_captain = df_starting['AT Captain'].copy()
                for i, name in enumerate(copy_of_at_fullname):
                    cap_symbol = '(c)'
                    name = str(name)
                    if cap_symbol in name:
                        copy_of_at_captain[i] = 1
                        new_name_a = name.split(cap_symbol)[0]
                        copy_of_at_fullname[i] = new_name_a
                df_starting['AT Fullname'] = copy_of_at_fullname
                df_starting['AT Captain'] = copy_of_at_captain

                # concate 2 df: df_hgoal and df_agoal into df_starting
                df_starting = pd.concat([df_starting, df_hgoal, df_agoal], axis=1)
                df_starting = df_starting.replace(to_replace=r'^\s+', value='', regex=True)
                df_starting = df_starting.replace(to_replace=r'\s+$', value='', regex=True)

                # check for row index of matched starname and fullname (of both AT, HT)
                row_value_dict = check_loc(df_starting,'Starname_h', 'Starname_a', 'HT Fullname', 'AT Fullname', 'Goal_eventh', 'Goal_eventa')

                copy_of_ht_goal = df_starting['HT Goal'].copy()
                for row in row_value_dict[0]:
                    value_h = row_value_dict[0][row]
                    copy_of_ht_goal.loc[row] = value_h
                df_starting['HT Goal'] = copy_of_ht_goal

                copy_of_at_goal = df_starting['AT Goal'].copy()
                for row in row_value_dict[1]:
                    value_a = row_value_dict[1][row]
                    copy_of_at_goal.loc[row] = value_a
                df_starting['AT Goal'] = copy_of_at_goal

                if rounds == 'qualification':
                    df_starting['HT Goal'] = df_starting['Goal_eventh']
                    df_starting['AT Goal'] = df_starting['Goal_eventa']
                    df_starting['HT Fullname'] = df_starting['Starname_h']
                    df_starting['AT Fullname'] = df_starting['Starname_a']

                # df_starting.drop(columns=['Starname_h', 'Starname_a', 'Goal_eventh', 'Goal_eventa'])


            # if no starting information
            else:
                df_starting = pd.DataFrame(None, columns=[
                    'MatchID', 'HT Role', 'HT Shirt Number',
                     'HT Fullname', 'HT Discipline', 'HT In_Out',
                     'AT Role',
                     'AT Shirt Number', 'AT Fullname',
                     'AT Discipline', 'AT In_Out'])
                for column in list(df_starting.columns):
                    df_starting.at[0, column] = 'missing'
                df_starting['MatchID'] = match_id

            # make df_matches for all collected data
            df_matches = pd.DataFrame(
                {'Year': [match_year], 'Stage': [match_stage],
                 'Date': [match_date], 'Time': [match_time],
                 'Stadium': [match_stadium], 'Location': [match_location],
                 'Home Team': [home_team_name],
                 'HT Goals': [home_team_f_score],
                 'AT Goals': [away_team_f_score],
                 'Away Team': [away_team_name],
                 'Match Attendance': [match_attendance],
                 'MatchID': [match_id],
                 'Refer': [match_refer]
                 })
            print(f'WorldCup {match_year} : {rounds} :: MatchID = {match_id}')

            # append collecting data of the current match to corresponding columns of sheet Match Details
            df_group_starting = pd.concat(
                    [df_group_starting, df_starting])

            # append collecting data of current match to corresponding columns of sheet All Matches
            df_group_matches = pd.concat([df_group_matches, df_matches])
        url_main = url_temp1

# export to file excel
df_group_matches.to_excel('Fifa_world_cup_allMatches.xlsx', sheet_name='All Matches')
df_group_starting.to_excel('Fifa_world_cup_matchDetails.xlsx', sheet_name='Match Details')
