from collections import Counter


class Solution:
    def checkInclusion(self, s1: str, s2: str) -> bool:
        aim_str=Counter(s1)
        left,right=0,0

        for i in range(len(s2)):

            aim_str[s2[i]]-=1

            while aim_str[s2[i]]<0:
                aim_str[s2[left]]+=1
                left+=1

            if right-left+1==len(s1):
                return True

        return False


s1 = "ab"
s2 = "eidbaooo"
S=Solution()
S.checkInclusion(s1,s2)
print(len(s2) - len(s1))
# print(list(s1).sort() == list(s2[len(s2) - len(s1):-1]).sort())
