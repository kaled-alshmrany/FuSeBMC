#include <MyOptions.h>

string MyOptions::GetLabelForFunc(string func)
{
    if(!this->addLabelInFunc)
        return "";
    map<string,string>::iterator it = this->funcLabelMap.find(func);
    if(it != this->funcLabelMap.end())
    {
        return  it->second;
    }
    return "";
}
