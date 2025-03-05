from .toolclass_version import SemVer
import datetime as dt
import numpy as np

class PyDocument:  # not intended for distribution
    __fullname = 'String Formatter for Python Document'
    __lastupdate = dt.datetime.strptime('2025-02-21', '%Y-%m-%d')
    __version = SemVer(0, 3, 1)
    __developer = {'name': 'DH.Koh'}
    __callsign = 'PyDoc'

    __dependency = {}

    def __init__(self, width: int = 120):
        self.width = width

    def f(self, string: str, tab: int = 0):
        string_copy = str(string)  # copy()
        for nlinebreak in range(5, 1, -1):
            string_copy = string_copy.replace('\n' * nlinebreak, f'\({nlinebreak})n')
        string_temp = string_copy.replace('\n', ' ')
        for nlinebreak in range(5, 1, -1):
            string_temp = string_temp.replace(f'\({nlinebreak})n', '\n' * (nlinebreak - 1))
        string_paragraphs = string_temp.split('\n')

        processed_width = self.width - tab * 4
        #==============================================================================================================

        string_paragraphs_processed = []
        for string_paragraph in string_paragraphs:
            if string_paragraph != '':
                string_paragraph_processed_arr = []
                string_paragraph_restpart = str(string_paragraph)
                while True:
                    string_paragraph_restpart_masks = [False] * len(string_paragraph_restpart)

                    if '\033' in string_paragraph_restpart:
                        for index in [index for index, char in enumerate(string_paragraph_restpart) if char == '\033']:
                            for index_offset in range(3, -1, -1):
                                string_paragraph_restpart_masks[index + index_offset] = True
                            # if string_paragraph_restpart_masks[index - 1] == False:
                            #     string_paragraph_restpart_masks[index] = True

                    string_paragraph_restpart_strlen = np.cumsum(~np.array(string_paragraph_restpart_masks))

                    if string_paragraph_restpart_strlen[-1] > processed_width:
                        index_front = np.where(string_paragraph_restpart_strlen > processed_width - 1)[0][0]
                        index_back = np.where(string_paragraph_restpart_strlen > processed_width)[0][0]

                        if string_paragraph_restpart[index_front] == ' ':  # '**** |*****'
                            index_scope = np.where(string_paragraph_restpart_strlen > processed_width - 2)[0][0]
                            if string_paragraph_restpart[index_scope] == ' ':  # '***  |*****'
                                """
                                [___ToDo**_] (25-02-18) - 줄 나누기 기준점 앞에 복수의 공백문자가 있을 때 중복 공백 어떻게 처리할 것인지?
                                """
                                index_scope = np.where(string_paragraph_restpart_strlen > processed_width - 3)[0][0]
                                string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_scope])
                                string_paragraph_restpart = string_paragraph_restpart[index_scope:]
                                """ ^^^^^^^^^^ temporal function ^^^^^^^^^^ """
                            else:  # '***a | ****'
                                string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_front])
                                string_paragraph_restpart = string_paragraph_restpart[index_front:]
                        elif string_paragraph_restpart[index_back] == ' ':  # '*****| ****'
                            string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_back])
                            string_paragraph_restpart = string_paragraph_restpart[index_back:]
                        else:  # '****a|a****'
                            index_scope = np.where(string_paragraph_restpart_strlen > processed_width - 2)[0][0]
                            if string_paragraph_restpart[index_scope] == ' ':  # '*** a|a****'
                                string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_scope])
                                string_paragraph_restpart = string_paragraph_restpart[index_scope:]
                            else:  # '***aa|a****'
                                index_scope = np.where(string_paragraph_restpart_strlen > processed_width - 3)[0][0]
                                if string_paragraph_restpart[index_scope] == ' ':  # '** aa|a****'
                                    index_scope_temp = np.where(string_paragraph_restpart_strlen > processed_width - 2)[0][0]
                                    if string_paragraph_restpart[index_scope_temp] in ['\'', '\"', '(', '{', '[', '<', '/']:  # '** (a|a****'
                                        string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_scope])
                                        string_paragraph_restpart = string_paragraph_restpart[index_scope:]
                                    else:  # '** aa|a****'
                                        string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_scope])
                                        string_paragraph_restpart = string_paragraph_restpart[index_scope:]
                                elif string_paragraph_restpart[index_scope] in ['\'', '\"', '(', '{', '[', '<', '/']:  # '**(aa|a****'
                                    index_scope_temp = np.where(string_paragraph_restpart_strlen > processed_width - 4)[0][0]
                                    if string_paragraph_restpart[index_scope_temp] == ' ':  # '* (aa|a****'
                                        string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_scope_temp])
                                        string_paragraph_restpart = string_paragraph_restpart[index_scope_temp:]
                                    else:  # '*a(aa|a****'
                                        string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_front] + '-')
                                        string_paragraph_restpart = string_paragraph_restpart[index_front:]
                                else:  # '**aaa|a****'
                                    string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart[:index_front] + '-')
                                    string_paragraph_restpart = string_paragraph_restpart[index_front:]

                        string_paragraph_restpart = string_paragraph_restpart[next((i for i, char in enumerate(string_paragraph_restpart) if char != ' '), -1):]
                    else:
                        string_paragraph_processed_arr.append(' ' * tab * 4 + string_paragraph_restpart)
                        break

                string_paragraphs_processed.append('\n'.join(string_paragraph_processed_arr))

        return '\n'.join(string_paragraphs_processed)

if __name__ == '__main__':
    doc = PyDocument()
    print(doc.f(
""" In the realm of Eldoria, nestled amidst rolling hills and ancient forests, lived Princess Elara, a maiden of unparalleled beauty and spirit.
Her laughter was like the tinkling of a silver bell, and her eyes sparkled like the stars in the night sky.
But her life was not without its shadows, for a fearsome dragon named \033[1m\033[4m\033[7mIgnis\033[0m dwelled in the nearby mountains, terrorizing the countryside and threatening the kingdom's peace.
Ignis was a creature of immense power, its scales as hard as steel, its claws as sharp as razors, and its breath a torrent of fire that could incinerate anything in its path.
The dragon had long been a scourge upon Eldoria, its fiery reign casting a pall over the land and instilling fear in the hearts of its people.
The king, Elara's father, had tried countless times to slay the beast, but all his knights and armies had failed, their weapons no match for the dragon's impenetrable hide and devastating flames.
And so, the kingdom lived in constant dread, wondering when the next fiery attack would come, when the dragon would once again descend from its mountain lair to wreak havoc upon their homes and lives.
Princess Elara, despite her gentle nature, possessed a fierce spirit and a deep love for her people.
She refused to cower in fear, refused to accept the dragon's tyranny as an inescapable fate.
She yearned for a hero, a champion who could vanquish the beast and bring peace back to Eldoria.

 One day, a noble knight named Sir Gideon arrived in Eldoria, his heart burning with courage and his sword gleaming with honor.
He had heard tales of the dragon's wrath and vowed to protect the princess and her kingdom from its fiery reign.
Sir Gideon was a man of unwavering loyalty and unwavering chivalry, his spirit as bright as his polished armor.
He was renowned throughout the land for his bravery and skill in battle, his name whispered with awe and respect by commoners and nobles alike.
He was a knight of the highest caliber, a true embodiment of the chivalric code, his every action guided by honor, courage, and a deep sense of justice.
When he arrived in Eldoria, his reputation preceded him, and the people greeted him with hope in their eyes, believing that he was the hero they had been waiting for, the one who could finally rid them of the dragon's menace.
Princess Elara, upon meeting Sir Gideon, was immediately struck by his noble bearing and the intensity of his gaze.
She saw in him a kindred spirit, a soul as pure and radiant as her own.
As they spent time together, their bond deepened, and a spark of love ignited in their hearts.
They shared long walks through the royal gardens, discussing matters of state and personal dreams, their conversations filled with laughter and shared silences that spoke volumes.
Elara found herself drawn to Gideon's strength and his unwavering belief in the good, while Gideon was captivated by Elara's compassion and her unwavering determination to protect her people.

 But their budding romance was threatened by the looming presence of Ignis.
The dragon's attacks grew bolder, its fiery breath scorching the land and casting a pall over the kingdom.
Sir Gideon knew he had to act, to face the beast and protect the woman he had come to cherish.
He could no longer stand by and watch the kingdom suffer, watch Elara live in fear.
He had to act, even if it meant facing the dragon alone.
He went to the king and offered his services, vowing to slay the dragon or die trying.
The king, though hesitant to send his bravest knight to what seemed like certain death, could not deny Gideon's plea.
He knew that the kingdom's hope rested on Gideon's shoulders, that if anyone could defeat the dragon, it was him.
And so, with a heavy heart but with a glimmer of hope, the king gave his blessing.
Before embarking on his perilous quest, Gideon sought out Elara, knowing that he could not leave without her blessing.
He found her in the royal chapel, praying for the kingdom's safety.
He knelt beside her, and they prayed together, their hearts intertwined, their love a silent plea for courage and protection.
When they rose, Gideon took Elara's hand, his touch gentle yet firm.
He told her of his plan, of his determination to face the dragon, not just for the kingdom but for her, for the love that had blossomed between them.
Elara, though fearful for his life, did not try to dissuade him.
She knew that this was his destiny, that he was the hero she and her people had been waiting for.
Instead, she offered him her blessing, her love a shield of protection around his heart.
She gave him a token of her affection, a small silver locket containing a strand of her hair, a reminder of the love that awaited him upon his return.

 With the princess's blessing and the kingdom's hopes resting on his shoulders, Sir Gideon ventured into the dragon's lair, a dark and treacherous cave hidden deep within the mountains.
He battled his way through hordes of monstrous creatures, his sword flashing like lightning, his spirit unyielding.
The cave was a labyrinth of winding tunnels and treacherous pitfalls, home to all manner of grotesque creatures that served as the dragon's minions.
Gideon fought his way through them, his sword a whirlwind of steel, his shield deflecting their claws and fangs.
He faced giant spiders, their webs sticky and strong, their venomous fangs dripping with poison.
He battled packs of goblins, their eyes beady and malicious, their gnarled fingers wielding rusty daggers.
He overcame each challenge, his resolve strengthened by the thought of Elara, by the love that burned within him.
Finally, he stood before Ignis, the dragon's eyes burning with malevolent fire.
The battle was fierce and unrelenting, the knight's courage matched only by the dragon's raw power.
Ignis was a terrifying sight, its massive form filling the cave, its scales shimmering like a thousand emeralds, its eyes burning with ancient malice.
It unleashed its fiery breath, a torrent of flames that engulfed the cave, forcing Gideon to dodge and weave, his shield raised in defense.
Gideon fought with the strength of his love for Princess Elara, his heart filled with the fire of his devotion.
He remembered her gentle smile, her kind words, her unwavering belief in him. He thought of the kingdom, of the people who lived in fear, of their hopes pinned on his success.
He channeled all his love, all his hopes, all his fears into his sword, each strike aimed with precision, each parrydeflecting the dragon's attacks.

 In the end, it was not brute force that prevailed, but the knight's unwavering spirit and the purity of his heart.
With a final, desperate strike, he pierced the dragon's heart, its roar echoing through the mountains as it fell lifeless to the ground.
The dragon's death was a moment of profound triumph, a victory not just for Gideon but for the entire kingdom.
The fiery reign of terror was finally over, the shadow that had loomed over Eldoria for so long was lifted.
Sir Gideon, exhausted but victorious, emerged from the dragon's lair, the dragon's heart clutched in his gauntleted hand.
He made his way back to Eldoria, his steps heavy but his heart light.
He was greeted as a hero, the people cheering his name, their faces filled with joy and relief.
The king embraced him, tears of gratitude streaming down his face.
But it was Elara's embrace that Gideon craved the most.
He found her in the throne room, surrounded by her court, her face radiant with happiness.
He knelt before her, offering her the dragon's heart as a symbol of his love and his victory.
She took it, her fingers brushing against his, her eyes filled with love and admiration.
She knew that he was not just a hero, but the man she was destined to be with.
They ruled Eldoria together, their reign marked by peace, prosperity, and the enduring spirit of chivalry.
Their love story became a legend, a tale told and retold through the ages, a testament to the power of love, courage, and sacrifice.
And so, the kingdom of Eldoria prospered, its people forever grateful to the noble knight who had slain the dragon and won the heart of their princess.
The end."""
    ))
