#allow ja,en

def to(lang,word):
	if lang=="en":
		return word
	elif lang=="ja":
		words = {
			"voted": "投票済み",
			"people": "人",
			"pair": "組",
			"Imposter Check": "imposterチェック",
			"Select 〇 if you are an imposter; select ✕ if you are a crewmate": "あなたがimposterの場合には〇を、crewmateの場合は✕を選択してください",
			"state": "ステータス",
			"**RUNNING**": "利用可能",
			"**STOPPING**": "停止中",
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
		}
		return words[word]