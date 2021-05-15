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
			"Only the representative should operate the system.":"代表者だけが操作してください",
			"Check the number of roles.": "人数が不足しています。\nもう一度試してください。",
			"How to use": "使い方",
			"move up": "上に移動",
			"move down": "下に移動",
			"increase by one person": "１人増やす",
			"reduce by one person": "１人減らす",
			"join the game": "ゲームに参加する",
			"start the game": "ゲームを開始する",
			"Please press only if you are an imposter.": "imposterのみ押してください",
			"Please push when all imposter people have voted.": "imposterが全員投票したら押してください",
			"Press when you are sure.": "確認したら押してください",
			"After the game starts, press this button to notify your opponent that you have died.": "ゲーム開始後、このボタンを押すと自分が死亡したことが相手に通知されます",
			"Select the alphabet of the player you want to divine": "占いたいプレイヤーのアルファベットを選択してください",
			"Press when the fortuneteller is about to act.": "占い師が行動するタイミングで押してください",
			"Press when the turn in which the fortuneteller can act ends.": "占い師が行動できるターンが終了したときに押してください",
			"Waiting for confirmation on the role.": "役職の確認を待っています",
		}
	}
	if lang in words and word in words[lang]:
		ans = words[lang][word]
	else:
		ans = word
	return ans
