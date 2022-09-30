from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Transit, ExtOrder, TransitSegment


class Command(BaseCommand):

    def __init__(self, queryset=None):
        super(Command, self).__init__(queryset)
        self.queryset = queryset if queryset else Transit.objects.all()

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

        for t, s in target:
            s.ordering_num = t + 1

        for s in qs:
            print(s.ordering_num)

        return qs.order_by('ordering_num')

    def __create_ext_orders_mapper(self, transit):
        ext_orders_mapper = list()
        if transit.segments.exists():
            qs = self.__sort_segments(transit.segments.all())
            ext_orders_mapper.append([qs[0]])
            for segment in qs[1:]:
                if segment.carrier != ext_orders_mapper[-1][-1].carrier:
                    ext_orders_mapper.append(list())
                ext_orders_mapper[-1].append(segment)
        return ext_orders_mapper

    def __create_ext_orders(self, mapper):
        transit = mapper[0][0].transit

        for t, segments_list in enumerate(mapper):

            ext_order = ExtOrder(
                number=f'{transit.order.client_number}/{transit.sub_number}-{t + 1}',
                date=timezone.now(),
                contractor=segments_list[0].carrier,
                from_addr=segments_list[0].from_addr,
                sender=transit.sender,
                to_addr=segments_list[-1].to_addr,
                receiver=transit.receiver
            )
            ext_order.segments.set(segments_list)
            ext_order.save()

            segments_list[0].update(sender=transit.sender)
            segments_list[-1].update(receiver=transit.receiver)

            for segment in segments_list:
                segment.order = transit.order
                segment.save()

    def handle(self, *args, **options):
        for transit in self.queryset:
            mapper = self.__create_ext_orders_mapper(transit)
            self.__create_ext_orders(mapper)
