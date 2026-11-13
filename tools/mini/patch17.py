"""One-off (web v175): the Miniature Mayhem Cup. The four toy tracks stop being 'special' (their layout scripts no longer
say special=1), which makes them tracks 20..23 = the sixth cup; this adds that cup's name and colour. Run once."""
P = 'D:/crust-rush/source/crust-rush.html'
s = open(P, encoding='utf-8', newline='').read()
a = "{name:'Neon Cup',col:'#3ff0ff'}];"
assert s.count(a) == 1 and 'Miniature Mayhem Cup' not in s
s = s.replace(a, "{name:'Neon Cup',col:'#3ff0ff'},{name:'Miniature Mayhem Cup',col:'#ff6a12'}];")
open(P, 'w', encoding='utf-8', newline='').write(s)
print('cup added')
