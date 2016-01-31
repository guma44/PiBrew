def save_config(path, params):
    with open(path, 'w') as out:
        for s in dir(params):
            if not s.startswith('__'):
                if type(getattr(params, s)) == type(0):
                    out.write("%s = %i\n" % (s, getattr(params, s)))
                elif type(getattr(params, s)) == type(0.0):
                    out.write("%s = %f\n" % (s, getattr(params, s)))
                elif type(getattr(params, s)) == type(''):
                    out.write('%s = "%s"\n' % (s, getattr(params, s)))
                else:
                    out.write("%s = %s\n" % (s, str(getattr(params, s))))
