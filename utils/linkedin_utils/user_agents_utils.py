# import userAgents from "./userAgents.json";

# /**
#  * Selects a random user-agent string from a predefined list.
#  * @returns {string} A random user-agent string.
#  */
# export const getUserAgent = () => {
#   const index = Math.floor(Math.random() * userAgents.length);
#   const userAgent = userAgents[index];
#   return userAgent;
# };


# write it's equivalent in python
import random
import data.user_agents as user_agents


def get_user_agent():
    index = random.randint(0, len(user_agents) - 1)
    user_agent = user_agents[index]
    return user_agent
