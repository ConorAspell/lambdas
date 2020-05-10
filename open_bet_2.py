import json
import requests
import smtplib, ssl

def get_spread(win_1=1.9, win_2=3.3, draw=4.1, spend=1000, min_profit=0):
    spend1 = int(spend/win_1)+1 #work out minimum needed to bet to get spend back
    spend2 = int(spend/win_2)+1
    solutions = []
    final_return = spend+min_profit #desired profit
    for i in range(spend1, spend): #goes to spend
        for j in range(spend2,spend): #goes to spend
            k = spend-i-j #draw variable
            if k < 0: #saves search space
                break
            return_1 = i*win_1
            return_2 = j*win_2 #3 potential return, want to all to be above final return
            return_3 = k*draw
            if return_1>=final_return and return_2>=final_return and return_3>=final_return:
                solution = {}
                solution['bets'] = [i,j,k]
                solution['potential_total'] = return_1+return_2+return_3 #need to choose best solution, highest return seems good idea
                solutions.append(solution.copy())
    if len(solutions) > 0:
        max_combo = max(solutions, key=lambda x:x['potential_total']) #lambda to pick out highest return
        return max_combo['bets']
    else:
        return False

def extract(api_key,sport_key = 'soccer'):
    odds_response = requests.get('https://api.the-odds-api.com/v3/odds/?apiKey=57020be3a218578f26407e53ed5501e8&sport='+sport_key+'&region=uk&mkt=h2h')   
    odds_json = json.loads(odds_response.text)
    if not odds_json['success']:
        print(
            'There was a problem with the odds request:',
            odds_json['msg']
        )
    else:
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_json

def transform(odds):
    every_odds =[]
    full_message = ""
    count = 0
    for event in odds['data']:
        all_events = []
        count+=1
        for site in event['sites']:
            all_odds = {}
            odd = site['odds']
            h2h = odd['h2h']
            if len(h2h) ==3:
                all_odds['site'] = site['site_key']
                all_odds['team_1'] = event['teams'][0]
                all_odds['team_2'] = event['teams'][1]
                all_odds['team_1_wins'] = h2h[0]
                all_odds['team_2_wins'] = h2h[1]
                all_odds['draw_wins'] = h2h[2]
                all_odds['event_id'] = count
                all_events.append(all_odds.copy())
        every_odds.append(all_events.copy())
    for game in every_odds:
        max_team_1 = max(game, key=lambda x:x['team_1_wins']) #lambda to pick out highest return
        max_team_2 = max(game, key=lambda x:x['team_2_wins']) #lambda to pick out highest return
        max_draw = max(game, key=lambda x:x['draw_wins']) #lambda to pick out highest return
        test = get_spread(max_team_1['team_1_wins'], max_team_2['team_2_wins'], max_draw['draw_wins'])
        if test:
            line1 = """---------------------------------------------
            Bet: """ + str(test[0]/10) + """ percent on """ + max_team_1['team_1'] + """ at """ + str(max_team_1['team_1_wins'])+ """ for a win of """ +str((test[0]*max_team_1['team_1_wins'])/10) + """ percent on """+ max_team_1['site']+ """ 
            Bet: """+ str(test[1]/10) + """ percent on """ + max_team_2['team_2'] + """ at """ + str(max_team_2['team_2_wins'])+ """ for a win of """ +str((test[1]*max_team_2['team_2_wins'])/10) + """ percent on """+ max_team_2['site'] + """ 
            Bet: """ + str(test[2]/10) + """ percent on draw at """ + str( max_draw['draw_wins']) + """ for a win of """ +str((test[2]*max_draw['draw_wins'])/10) + """ percent on """+ max_draw['site']+ """
            ---------------------------------------------"""
            message = line1 
            print(message)
            full_message = full_message + message
    return full_message

def load(message):
 
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "conor.aspell.94@gmail.com"  # Enter your address
    receiver_email ="conor.aspell.1994@gmail.com"  # Enter receiver address
    password =  "4562433Ss"

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
   

def lambda_handler(event, context):
    final_message = ""
    api_key = '57020be3a218578f26407e53ed5501e8'
    sports_response = requests.get(' https://api.the-odds-api.com/v3/sports/?apiKey='+api_key)
    sports_json = json.loads(sports_response.text)
    soccer_leagues = []
    for sport in sports_json['data']:
        if 'soccer' in sport['key']:
            soccer_leagues.append(sport['key'])
    print(soccer_leagues)
    for item in soccer_leagues:    
        odds = extract(api_key, item)
        final_message = final_message + transform(odds)
        final_message.encode('ascii', 'ignore')
    load(final_message)
