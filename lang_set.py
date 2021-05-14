#allow ja,en

def to(lang,word):
	words = {
		"en": {
		},
		"ja": {
			"voted": "投票済み",
			"people": "人",
			"pair": "組",
			"Imposter Check": "imposterチェック",
			"Select 〇 if you are an impostor.": "あなたがimposterの場合には〇を選択してください",
			"state": "ステータス",
			"RUNNING": "利用可能",
			"STOPPING": "停止中",
			"teruteru": "てるてる",
			"madmate": "狂人",
			"lovers": "恋人",
			"spy": "スパイ",
			"diviner": "占い師",
			"Lovey-dovey❤":"ラブラブですね❤",
			"Let's outsmart everyone!":"みんなを出し抜きましょう",
			"You": "あなた",
			"Let's find the imposter.":"imposterを探し出そう",
			"Let's cooperate with imposter.": "imposterに協力しましょう",
			"Let's fortunate.": "気になる人を占おう",
			"ROLE": "役職",
			"Role confirmation complete.": "役職の確認を完了しました",
			"GAME START!!": "ゲームスタート！",
			"The number of participants is too small for the role.":"役職に対して参加人数が少なすぎます",
			"It is currently under maintenance. Please wait for a while.":"ただいまメンテナンス中です。しばらくお待ちください。",
			"dead": "死亡",
			"List of roles": "役職一覧",
			"List of Participants": "参加者一覧",
			"Fortune Teller's Action": "占い師のアクション",
			"The GM should press the button when the fortuneteller is ready to act.":"占い師が行動するタイミングでGMがボタンを押してください",
		}
	}
	if lang in words and word in words[lang]:
		ans = words[lang][word]
	else:
		ans = word
	return ans
