'''
prop_parser.py  ver. 0.1

(C) Conrad Heidebrecht (github.com/eternali) 10 Feb 2018

'''

from datetime import datetime
import os
import time


class Property:
    '''
    Data class containing the property value and the comments corresponding to it.

    '''

    def __init__(self, prop, comments=[]):
        self.prop = prop
        self.comments = comments[:]  # copy comments by value, not reference


class PropParser:
    '''
    PropParser is a properties parser that explicitly supports hierarchical document structure.
    Levels of property hierarchy is denoted by '.' in the property name.
    For example:
        a.b = 12
        a.c=test
        d=321
    will be parsed to be available as a dictionary:
        {
            'a': {
                'b': '12',
                'c': 'test'
            },
            'd': 321
        }

    You can nest as many levels as you like, however the root property of a hierarchy must not be explicitly set.
    For example the following will raise an error:
        a = 123
        a.b = test
    This is because 'a' is initially set to an integer, but then wants to be reassigned to a dictionary.

    You can also (optionally) parse comments included in the properties file (you can customize what is parsed 
    as a comment with the COMMENT parameter in the constructor).
    Note: a line can either be a property or a comment, you cannot have an inline comments
    i.e. `a.b=123 #comment` is invalid, but
         `#comment
          a.b=123` is what you should be doing.
    If comments are included in property parsing, you can access them through the comments property,

    e.g. 

    #comment one
    a.b=123
    a.c=value
    #comment two
    b.d=number

    will be parsed as

    {
        'a': {
            'b': '123' (comments='comment one')
            'c': 'value'
        },
        'b': {
            'd': 'number (comments='comment two')
        }
    }

    To access a.b's value, nothing changes (just do properties['a']['b'] and you will get '123'),
    and to get a.b's comments, you can simply do properties['a']['b'].comments
    Note: the way comments are parsed is they are stored in the first property below it (as seen in the example)

    '''

    def __init__(self, load_file, COMMENT='#'):
        # allows for custom comment denotation
        self.COMMENT = COMMENT
        self.__properties__ = {}
        if load_file is not None:
            self.load(load_file)

    def __setitem__(self, key, value):
        self.__properties__[key].prop = value

    def __getitem__(self, key):
        p = self.__properties__.get(key)
        if type(p) is dict:
            print('think is dict')
            return p
        else:
            return p.prop

    def __contains__(self, key):
        return key in self.__properties__.keys()

    def load(self, filename):
        self.__properties__ = {}
        
        if not os.path.isfile(filename):
            return False
        
        with open(filename, 'r') as f:
            cached_comments = []
            for n, l in enumerate(f):
                line = l.rstrip(os.linesep).strip('\t')
                if line.startswith(self.COMMENT):
                    cached_comments.append(line.strip(self.COMMENT).strip(' '))
                    continue
                if len(line) < 2 or '=' not in line:
                    continue
                line = line.split('=', 1)
                key = line[0].strip()
                value = line[1].strip() if len(line) > 1 else ''
                self.__parse_prop(self.__properties__, cached_comments, key.split('.'), value)
        
        return True

    def __parse_prop(self, props, comments, keys, value):
        if keys[0] in props.keys():
            self.__parse_prop(props[keys[0]], comments, keys[1:], value)
        elif len(keys) > 1:
            props[keys[0]] = {}
            self.__parse_prop(props[keys[0]], comments, keys[1:], value)
        else:
            # save the final value and reset the comments for the next property
            props[keys[0]] = Property(value, comments)
            del comments[:]

    def save(self, filename, timestamp=True, comments=True):
        # formatted timestamp example: 'Sat Feb 10 16:07:17 EST 2018'
        # note datetime's strftime %Z interpolation only returns a nonempty string if
        # it is not a default zone (whatever that means), so I'm just using time.strftime's
        ts = datetime.now().strftime('%a %b %d %H:%M:%S {} %Y'.format(time.strftime('%Z')))
        filename = (os.getcwd() + '/' if not filename.startswith('/') else '') + filename
        if not os.path.exists(filename.rsplit('/', 1)[0]):
            os.makedirs(filename.rsplit('/', 1)[0])

        with open(filename, 'w+') as f:
            if timestamp:
                f.write(self.COMMENT + ts)
            compiled = []
            self.__build(self.__properties__, '', compiled, incl_comments=comments)
            f.write('\n'.join(compiled))

    def __build(self, prop, cur_line, compiled, incl_comments=True):
        if isinstance(prop, dict):
            for key in prop.keys():
                self.__build(prop[key], cur_line + ('.' if cur_line else '') + str(key), compiled)
        else:
            if incl_comments:
                compiled += [self.COMMENT + comment for comment in prop.comments]
            compiled.append(cur_line + '=' + prop.prop)
        

