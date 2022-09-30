from django.core.management.base import BaseCommand
from orders.models import Transit


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Transit.objects.all()

    def __enumerate_segments(self, transit):
        if transit.segments.filter(ordering_num=None).exists():
            print(transit, 'processed')
            qs = transit.segments.all()
            for t, i in self.__sort_segments(qs):
                i.ordering_num = t + 1
                i.save()

    @staticmethod
    def __sort_segments(qs):
        mid, target = [], []
        first, last = None, None
        for i in qs:
            if not qs.filter(to_addr=i.from_addr).exists():
                if first is not None:
                    print(first.transit, 'contains wrong segments')
                    return enumerate([])
                first = i
            elif not qs.filter(from_addr=i.to_addr).exists():
                if last is not None:
                    print(first.transit, 'contains wrong segments')
                    return enumerate([])
                last = i
            else:
                mid.append(i)
        target.append(first)
        while mid:
            l = len(mid)
            for i in mid.copy():
                if i.from_addr == target[-1].to_addr:
                    target.append(i)
                    mid.remove(i)
            print(l, '-', len(mid))
            if len(mid) == l:
                print(first.transit, 'contains wrong segments')
                return enumerate([])
        target.append(last)

        return enumerate(target)

    def handle(self, *args, **options):
        for transit in self.queryset:
            self.__enumerate_segments(transit)

