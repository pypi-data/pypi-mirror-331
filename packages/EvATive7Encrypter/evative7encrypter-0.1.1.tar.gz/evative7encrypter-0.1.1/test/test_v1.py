from evative7enc import *

long_text = """
你说得对，但是一个不听群青シグナル的人，无非只有两种可能性。一种是没有能力听群青シグナル。因为买不起高配的耳机等各种自身因素，他的人生都是失败的，第二种可能：有能力却不听群青シグナル的人，在有能力而没有听群青シグナル的想法时，那么这个人的思想境界便低到了一个令人发指的程度。一个有能力的人不付出行动来证明自己，只能证明此人行为素质修养之低下。是灰暗的，是不被真正的社会认可的。
你說得對，但是一個不聽群青シグナル的人，無非只有兩種可能性。一種是沒有能力聽群青シグナル。因為買不起高配的耳機等各種自身因素，他的人生都是失敗的，第二種可能：有能力卻不聽群青シグナル的人，在有能力而沒有聽群青シグナル的想法時，那麼這個人的思想境界便低到了一個令人髮指的程度。一個有能力的人不付出行動來證明自己，只能證明此人行為素質修養之低下。是灰暗的，是不被真正的社會認可的。
You are right, but there are only two possibilities for a person who does not listen to 群青シグナル. One possibility is that he is not capable of listening to 群青シグナル. Because of various personal factors such as not being able to afford high-end headphones, his life is a failure. The second possibility is that a person who is capable but does not listen to 群青シグナル. When a person is capable but does not listen to 群青シグナル's ideas, then this person's ideological realm is so low that it is outrageous. A capable person who does not take action to prove himself can only prove that this person's behavior quality is low. It is gloomy and is not recognized by the real society.
あなたは正しいですが、『群青シグナル』 に耳を傾けない人には、2 つの可能性しかありません。一つは『群青シグナル』を聴けないこと。高級ヘッドフォンを買う余裕がないなどの個人的な理由で、彼の人生は失敗している。2つ目の可能性：能力はあるが『群青シグナル』を聴かない人。能力はあるが『群青シグナル』を聴かない人。ウルトラマリン・シグナーの考えを否定するなら、この人々の思想レベルはとんでもないレベルまで低下している。有能な人が自分自身を証明するために行動を起こさなければ、それは彼の行動の質と教養が低いことを証明するだけです。それは暗いものであり、現実の社会では認識されていません。
"""


def _testv1(model: EvATive7ENCv1 | EvATive7ENCv1Short):
    key = model.key()
    origin = long_text

    encoded = model.encode_to_evative7encformatv1(key, origin)
    assert encoded is not None

    decoded = model.decode_from_evative7encformatv1(encoded)
    assert decoded == origin


def test_EvATive7ENCv1():
    _testv1(EvATive7ENCv1)


def test_EvATive7ENCv1Short():
    _testv1(EvATive7ENCv1Short)
